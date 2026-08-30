from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid
import json
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models.live_state import (
    EntityVersion, AdvancedConflictRecord, ConflictResolutionType, EntityRevision
)
from app.models.task import Task
from app.models.agent_memory import AgentMemoryItem
from app.services.event_bus import event_bus
from app.core.exceptions import ValidationError, NotFoundError
from app.core.logging import logger

class ConflictEngine:
    """
    Motor Avançado de Resolução de Conflitos e Delta Sync (Fase 32).
    Implementa:
    - Versionamento estrito por entidade (base_version -> resulting_version)
    - Merge determinístico campo-a-campo (Non-conflicting / Field conflict merge)
    - Merge determinístico para conteúdo de texto inspirado em 3-way/CRDT
    - Registro e quarentena de conflitos não resolvidos (USER_REQUIRED)
    - Histórico de revisões e capacidade de restauração com auditoria
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    def calculate_checksum(self, payload: Dict[str, Any]) -> str:
        serialized = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    async def get_or_create_entity_version(
        self,
        entity_type: str,
        entity_id: str,
        initial_payload: Optional[Dict[str, Any]] = None
    ) -> EntityVersion:
        stmt = select(EntityVersion).where(
            EntityVersion.entity_type == entity_type,
            EntityVersion.entity_id == str(entity_id)
        )
        res = await self.db.execute(stmt)
        ev = res.scalar_one_or_none()

        if not ev:
            payload = initial_payload or {}
            ev = EntityVersion(
                entity_type=entity_type,
                entity_id=str(entity_id),
                version=1,
                checksum=self.calculate_checksum(payload),
                updated_by_device="DESKTOP-MAIN",
                last_payload=payload,
                updated_at=datetime.utcnow()
            )
            self.db.add(ev)
            await self.db.commit()
            await self.db.refresh(ev)
        return ev

    async def record_revision(
        self,
        entity_type: str,
        entity_id: str,
        version: int,
        device_id: str,
        snapshot_payload: Dict[str, Any],
        change_summary: Optional[str] = None
    ) -> EntityRevision:
        rev = EntityRevision(
            revision_id=f"rev_{uuid.uuid4().hex[:10]}",
            entity_type=entity_type,
            entity_id=str(entity_id),
            version=version,
            device_id=device_id,
            snapshot_payload=snapshot_payload,
            change_summary=change_summary or f"Versão {version} atualizada por {device_id}",
            created_at=datetime.utcnow()
        )
        self.db.add(rev)
        await self.db.commit()
        await self.db.refresh(rev)
        return rev

    async def apply_delta(
        self,
        device_id: str,
        entity_type: str,
        entity_id: str,
        base_version: int,
        delta_payload: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        Aplica delta determinístico.
        Retorna (sucesso, payload_final, conflict_id_se_houver).
        """
        now = datetime.utcnow()
        current_ev = await self.get_or_create_entity_version(entity_type, entity_id, delta_payload)
        current_payload = current_ev.last_payload or {}

        # 1. Sem conflito de versão (Fast-Forward)
        if base_version == current_ev.version:
            merged_payload = {**current_payload, **delta_payload}
            current_ev.version += 1
            current_ev.updated_by_device = device_id
            current_ev.last_payload = merged_payload
            current_ev.checksum = self.calculate_checksum(merged_payload)
            current_ev.updated_at = now

            await self.record_revision(
                entity_type=entity_type,
                entity_id=entity_id,
                version=current_ev.version,
                device_id=device_id,
                snapshot_payload=merged_payload,
                change_summary=f"Atualização direta v{current_ev.version}"
            )
            await self.db.commit()
            return True, merged_payload, None

        # 2. Conflito detectado (base_version != current_ev.version)
        # Tentativa de Merge Determinístico
        can_auto_merge, merged_payload, conflict_type = self._attempt_deterministic_merge(
            current_payload, delta_payload
        )

        if can_auto_merge and merged_payload is not None:
            # Auto merge bem sucedido
            current_ev.version += 1
            current_ev.updated_by_device = device_id
            current_ev.last_payload = merged_payload
            current_ev.checksum = self.calculate_checksum(merged_payload)
            current_ev.updated_at = now

            await self.record_revision(
                entity_type=entity_type,
                entity_id=entity_id,
                version=current_ev.version,
                device_id=device_id,
                snapshot_payload=merged_payload,
                change_summary=f"Auto-merge determinístico v{current_ev.version} ({conflict_type})"
            )

            # Grava registro do conflito resolvido automaticamente para auditoria
            conflict_id = f"conf_{uuid.uuid4().hex[:8]}"
            conflict_rec = AdvancedConflictRecord(
                conflict_id=conflict_id,
                entity_type=entity_type,
                entity_id=str(entity_id),
                base_version=base_version,
                local_version=current_ev.version - 1,
                remote_version=base_version + 1,
                local_payload=current_payload,
                remote_payload=delta_payload,
                merged_payload=merged_payload,
                conflict_type=conflict_type,
                resolution=ConflictResolutionType.AUTO_MERGED,
                is_resolved=True,
                resolved_by_device=device_id
            )
            self.db.add(conflict_rec)
            await self.db.commit()

            await event_bus.publish("SYNC_CONFLICT_RESOLVED", {
                "conflict_id": conflict_id,
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "resolution": "AUTO_MERGED"
            })
            return True, merged_payload, None

        # 3. Conflito irreconciliável automaticamente -> USER_REQUIRED
        conflict_id = f"conf_{uuid.uuid4().hex[:8]}"
        conflict_rec = AdvancedConflictRecord(
            conflict_id=conflict_id,
            entity_type=entity_type,
            entity_id=str(entity_id),
            base_version=base_version,
            local_version=current_ev.version,
            remote_version=base_version + 1,
            local_payload=current_payload,
            remote_payload=delta_payload,
            conflict_type=conflict_type,
            resolution=ConflictResolutionType.USER_REQUIRED,
            is_resolved=False
        )
        self.db.add(conflict_rec)
        await self.db.commit()

        await event_bus.publish("SYNC_CONFLICT_DETECTED", {
            "conflict_id": conflict_id,
            "entity_type": entity_type,
            "entity_id": str(entity_id),
            "device_id": device_id
        })
        return False, current_payload, conflict_id

    def _attempt_deterministic_merge(
        self,
        local_payload: Dict[str, Any],
        remote_payload: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Merge determinístico 3-way / field-level:
        Se campos modificados forem disjuntos -> mescla os campos.
        Se campo em comum for texto com adições lineares -> mescla linhas.
        Caso contrário -> requer intervenção do usuário.
        """
        local_keys = set(local_payload.keys())
        remote_keys = set(remote_payload.keys())
        all_keys = local_keys.union(remote_keys)

        merged = {}
        has_content_conflict = False

        for k in all_keys:
            in_local = k in local_payload
            in_remote = k in remote_payload

            if in_local and not in_remote:
                merged[k] = local_payload[k]
            elif not in_local and in_remote:
                merged[k] = remote_payload[k]
            else:
                # Campo presente em ambos
                val_loc = local_payload[k]
                val_rem = remote_payload[k]

                if val_loc == val_rem:
                    merged[k] = val_loc
                elif isinstance(val_loc, str) and isinstance(val_rem, str):
                    # Merge determinístico de texto linear (se um contém o outro como prefixo/adição)
                    if val_loc.strip() in val_rem:
                        merged[k] = val_rem # Remoto contém a expansão
                    elif val_rem.strip() in val_loc:
                        merged[k] = val_loc # Local contém a expansão
                    else:
                        # Conflito de conteúdo real no mesmo campo
                        has_content_conflict = True
                else:
                    has_content_conflict = True

        if has_content_conflict:
            return False, None, "CONTENT_CONFLICT"

        return True, merged, "FIELD_CONFLICT"

    async def resolve_conflict_manually(
        self,
        conflict_id: str,
        resolution: str,
        resolved_by_device: str = "DESKTOP-MAIN",
        merged_payload: Optional[Dict[str, Any]] = None
    ) -> AdvancedConflictRecord:
        stmt = select(AdvancedConflictRecord).where(AdvancedConflictRecord.conflict_id == conflict_id)
        res = await self.db.execute(stmt)
        conflict = res.scalar_one_or_none()

        if not conflict:
            raise NotFoundError("Conflito não encontrado.")

        if conflict.is_resolved:
            return conflict

        ev = await self.get_or_create_entity_version(conflict.entity_type, conflict.entity_id)
        final_payload = {}

        if resolution == "LOCAL_WON":
            final_payload = conflict.local_payload
            conflict.resolution = ConflictResolutionType.LOCAL_WON
        elif resolution == "REMOTE_WON":
            final_payload = conflict.remote_payload
            conflict.resolution = ConflictResolutionType.REMOTE_WON
        elif resolution in ["AUTO_MERGED", "USER_MERGE"]:
            final_payload = merged_payload or conflict.local_payload
            conflict.resolution = ConflictResolutionType.AUTO_MERGED
        else:
            final_payload = conflict.local_payload
            conflict.resolution = ConflictResolutionType.LOCAL_WON

        conflict.merged_payload = final_payload
        conflict.is_resolved = True
        conflict.resolved_by_device = resolved_by_device

        # Atualiza a entidade oficial
        ev.version += 1
        ev.last_payload = final_payload
        ev.checksum = self.calculate_checksum(final_payload)
        ev.updated_by_device = resolved_by_device
        ev.updated_at = datetime.utcnow()

        await self.record_revision(
            entity_type=conflict.entity_type,
            entity_id=conflict.entity_id,
            version=ev.version,
            device_id=resolved_by_device,
            snapshot_payload=final_payload,
            change_summary=f"Conflito resolvido manualmente ({resolution})"
        )

        await self.db.commit()
        await self.db.refresh(conflict)

        await event_bus.publish("SYNC_CONFLICT_RESOLVED", {
            "conflict_id": conflict_id,
            "entity_type": conflict.entity_type,
            "entity_id": conflict.entity_id,
            "resolution": resolution
        })
        return conflict

    async def list_pending_conflicts(self) -> List[AdvancedConflictRecord]:
        stmt = select(AdvancedConflictRecord).where(
            AdvancedConflictRecord.is_resolved == False
        ).order_by(desc(AdvancedConflictRecord.created_at))
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_entity_revisions(self, entity_type: str, entity_id: str) -> List[EntityRevision]:
        stmt = select(EntityRevision).where(
            EntityRevision.entity_type == entity_type,
            EntityRevision.entity_id == str(entity_id)
        ).order_by(desc(EntityRevision.version))
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
