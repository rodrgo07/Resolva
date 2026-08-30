import uuid
import secrets
import json
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_

from app.models.device import Device, DeviceSession, PairingRequest, SyncOperation, DevicePlatform, DeviceStatus
from app.models.task import Task
from app.models.calendar import CalendarEvent
from app.models.notification import Notification
from app.models.activity import ActivityLog
from app.schemas.device import (
    PairingStartResponse, PairingCompleteRequest, PairingCompleteResponse,
    SyncPushItem, SyncPushResponse, SyncPullResponse, MobileBootstrapResponse
)
from app.core.exceptions import ValidationError, PermissionError, NotFoundError
from app.automation.kill_switch import is_kill_switch_active
from app.core.logging import logger

class DeviceManager:
    """
    Gerenciador de Identidade de Dispositivos, Handshake de Pareamento Seguro
    e Validação de Sessões do RESOLVA MOBILE.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_devices(self) -> List[Device]:
        stmt = select(Device).where(Device.status != DeviceStatus.REVOKED).order_by(Device.last_seen_at.desc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_device_by_device_id(self, device_id: str) -> Optional[Device]:
        stmt = select(Device).where(Device.device_id == device_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def start_pairing(self, server_endpoint: str = "http://127.0.0.1:8700") -> PairingStartResponse:
        # Gera código numérico amigável de 6 dígitos formatado (ex: 847291)
        code_int = secrets.randbelow(900000) + 100000
        pairing_code = str(code_int)
        nonce = secrets.token_hex(16)
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        desktop_device_id = "RESOLVA-DESKTOP-MAIN"

        qr_data = {
            "version": "1.0",
            "pairing_code": pairing_code,
            "nonce": nonce,
            "server_endpoint": server_endpoint,
            "desktop_device_id": desktop_device_id,
            "expires_at": expires_at.isoformat()
        }
        qr_payload = json.dumps(qr_data)

        # Remove requisições pendentes expiradas
        await self.db.execute(
            delete(PairingRequest).where(
                or_(PairingRequest.expires_at < datetime.utcnow(), PairingRequest.status != "PENDING")
            )
        )

        req = PairingRequest(
            pairing_code=pairing_code,
            qr_payload=qr_payload,
            nonce=nonce,
            status="PENDING",
            expires_at=expires_at,
            desktop_device_id=desktop_device_id,
            server_endpoint=server_endpoint
        )
        self.db.add(req)
        await self.db.commit()

        return PairingStartResponse(
            pairing_code=pairing_code,
            qr_payload=qr_payload,
            nonce=nonce,
            expires_at=expires_at,
            server_endpoint=server_endpoint,
            desktop_device_id=desktop_device_id
        )

    async def complete_pairing(self, req_in: PairingCompleteRequest) -> PairingCompleteResponse:
        now = datetime.utcnow()
        # Busca requisição pendente por código ou nonce
        conditions = [PairingRequest.status == "PENDING", PairingRequest.expires_at >= now]
        if req_in.pairing_code:
            clean_code = req_in.pairing_code.replace(" ", "").strip()
            conditions.append(PairingRequest.pairing_code == clean_code)
        elif req_in.nonce:
            conditions.append(PairingRequest.nonce == req_in.nonce)

        stmt = select(PairingRequest).where(and_(*conditions))
        res = await self.db.execute(stmt)
        pairing_req = res.scalar_one_or_none()

        if not pairing_req:
            raise ValidationError("Código ou sessão de pareamento inválida ou expirada.")

        # Marca como CLAIMED (Uso único garantido)
        pairing_req.status = "CLAIMED"

        # Gera Device ID e Tokens de Sessão Seguros
        mobile_device_id = req_in.device_id or f"RESOLVA-MOBILE-{uuid.uuid4().hex[:8].upper()}"
        session_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(48)
        session_expires = now + timedelta(days=30)

        # Cria ou Atualiza Registro do Dispositivo
        device = await self.get_device_by_device_id(mobile_device_id)
        if not device:
            platform_enum = DevicePlatform.ANDROID if req_in.platform.upper() == "ANDROID" else DevicePlatform.IOS
            device = Device(
                device_id=mobile_device_id,
                device_name=req_in.device_name,
                platform=platform_enum,
                app_version=req_in.app_version,
                status=DeviceStatus.ACTIVE,
                is_trusted=True,
                last_seen_at=now,
                paired_at=now
            )
            self.db.add(device)
            await self.db.flush()
        else:
            device.status = DeviceStatus.ACTIVE
            device.device_name = req_in.device_name
            device.last_seen_at = now

        # Cria Sessão
        session = DeviceSession(
            device_id=device.id,
            session_token=session_token,
            refresh_token=refresh_token,
            expires_at=session_expires,
            is_revoked=False
        )
        self.db.add(session)

        # Auditoria
        audit = ActivityLog(
            type="device",
            action="device_paired",
            description=f"Dispositivo '{device.device_name}' ({device.device_id}) pareado com sucesso.",
            metadata_json={"device_id": device.device_id, "platform": device.platform.value}
        )
        self.db.add(audit)
        await self.db.commit()

        return PairingCompleteResponse(
            success=True,
            device_id=device.device_id,
            device_name=device.device_name,
            session_token=session_token,
            refresh_token=refresh_token,
            expires_at=session_expires,
            desktop_status={
                "status": "ONLINE",
                "version": "0.1.0",
                "backend": "ONLINE",
                "agent": "READY",
                "kill_switch": is_kill_switch_active()
            }
        )

    async def rename_device(self, device_id: str, new_name: str) -> Device:
        device = await self.get_device_by_device_id(device_id)
        if not device:
            raise NotFoundError("Dispositivo não encontrado.")
        device.device_name = new_name
        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def revoke_device(self, device_id: str) -> bool:
        device = await self.get_device_by_device_id(device_id)
        if not device:
            raise NotFoundError("Dispositivo não encontrado.")

        device.status = DeviceStatus.REVOKED
        device.is_trusted = False

        # Invalida todas as sessões
        await self.db.execute(
            update(DeviceSession).where(DeviceSession.device_id == device.id).values(is_revoked=True)
        )

        audit = ActivityLog(
            type="device",
            action="device_revoked",
            description=f"Acesso do dispositivo '{device.device_name}' ({device.device_id}) foi revogado.",
            metadata_json={"device_id": device.device_id}
        )
        self.db.add(audit)
        await self.db.commit()
        return True
