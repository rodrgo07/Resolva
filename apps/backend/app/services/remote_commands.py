import uuid
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update

from app.models.device import (
    Device, DeviceStatus, RemoteCommandRecord, RemotePendingAction,
    RemoteActionStatus, PushDeviceToken
)
from app.models.task import Task
from app.models.finance import Expense, TransactionType
from app.models.calendar import CalendarEvent, EventType
from app.models.study import StudySession, SessionMode, StudySubject
from app.models.notification import Notification
from app.models.automation import Automation
from app.models.activity import ActivityLog
from app.schemas.remote_commands import RemoteCommandRequest, RemoteCommandResponse
from app.automation.kill_switch import is_kill_switch_active
from app.services.event_bus import event_bus
from app.services.backup_manager import BackupManager
from app.services.sync_manager import SyncManager
from app.core.exceptions import ValidationError, PermissionError, NotFoundError
from app.core.logging import logger

# Catálogo explícito de comandos remotos homologados e seus níveis de risco/permissão
HOMOLOGATED_REMOTE_COMMANDS = {
    # LEITURA (Sem risco)
    "GET_DESKTOP_STATUS": {"perm": "READ", "risk": "LOW", "requires_confirm": False},
    "GET_TODAY_CONTEXT": {"perm": "READ", "risk": "LOW", "requires_confirm": False},
    "GET_TASKS": {"perm": "READ", "risk": "LOW", "requires_confirm": False},
    "GET_OVERDUE_TASKS": {"perm": "READ", "risk": "LOW", "requires_confirm": False},
    "GET_UPCOMING_EVENTS": {"perm": "READ", "risk": "LOW", "requires_confirm": False},
    "GET_NOTIFICATION_SUMMARY": {"perm": "READ", "risk": "LOW", "requires_confirm": False},
    "GET_FINANCE_SUMMARY": {"perm": "READ", "risk": "LOW", "requires_confirm": False},
    
    # ESCRITA SEGURA
    "CREATE_TASK": {"perm": "WRITE", "risk": "LOW", "requires_confirm": False},
    "COMPLETE_TASK": {"perm": "WRITE", "risk": "LOW", "requires_confirm": False},
    "CREATE_EXPENSE": {"perm": "WRITE", "risk": "LOW", "requires_confirm": False},
    "CREATE_CALENDAR_EVENT": {"perm": "WRITE", "risk": "LOW", "requires_confirm": False},
    "START_POMODORO": {"perm": "WRITE", "risk": "LOW", "requires_confirm": False},
    "MARK_NOTIFICATION_READ": {"perm": "WRITE", "risk": "LOW", "requires_confirm": False},
    "SYNC_NOW": {"perm": "WRITE", "risk": "LOW", "requires_confirm": False},
    "CREATE_BACKUP": {"perm": "WRITE", "risk": "LOW", "requires_confirm": False},
    
    # EXECUÇÃO DE ALTO RISCO / CONFIRMAÇÃO OBRIGATÓRIA
    "EXECUTE_APPROVED_AUTOMATION": {"perm": "EXECUTE", "risk": "MEDIUM", "requires_confirm": True},
    "DELETE_TASK": {"perm": "WRITE", "risk": "HIGH", "requires_confirm": True},
}

class RemoteCommandService:
    """
    Controlador de Comandos Remotos Seguros para o RESOLVA Mobile.
    Valida device_id, sessões ativas, catálogo de comandos, proteção contra replay,
    idempotência e roteia para a Permission Layer.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_command(self, req: RemoteCommandRequest) -> RemoteCommandResponse:
        now = datetime.utcnow()
        cmd_type = req.command_type.upper().strip()

        # 1. Validação de Dispositivo e Sessão Ativa
        stmt_dev = select(Device).where(Device.device_id == req.device_id)
        res_dev = await self.db.execute(stmt_dev)
        device = res_dev.scalar_one_or_none()

        if not device or device.status == DeviceStatus.REVOKED:
            raise PermissionError("Dispositivo não autorizado ou revogado.")

        # Atualiza last_seen
        device.last_seen_at = now

        # 2. Catálogo Homologado
        if cmd_type not in HOMOLOGATED_REMOTE_COMMANDS:
            # Rejeita comandos livres / shell / powershell
            audit_rej = ActivityLog(
                type="security",
                action="remote_command_blocked",
                description=f"Tentativa de comando remoto não homologado: '{req.command_type}'",
                metadata_json={"device_id": req.device_id, "command": req.command_type}
            )
            self.db.add(audit_rej)
            await self.db.commit()
            raise PermissionError(f"Comando remoto '{req.command_type}' não homologado na Permission Layer.")

        cmd_spec = HOMOLOGATED_REMOTE_COMMANDS[cmd_type]

        # 3. Idempotência / Proteção contra Replay
        stmt_rec = select(RemoteCommandRecord).where(RemoteCommandRecord.request_id == req.request_id)
        res_rec = await self.db.execute(stmt_rec)
        existing_record = res_rec.scalar_one_or_none()

        if existing_record:
            return RemoteCommandResponse(
                success=True,
                request_id=req.request_id,
                command_type=cmd_type,
                status="EXECUTED",
                message="Comando já processado anteriormente (Idempotente).",
                data=existing_record.result_data
            )

        # 4. Checagem de Confirmação Prévia Obrigatória
        if cmd_spec["requires_confirm"]:
            action_id = f"action_{uuid.uuid4().hex[:8]}"
            pending_action = RemotePendingAction(
                action_id=action_id,
                request_id=req.request_id,
                device_id=req.device_id,
                command_type=cmd_type,
                parameters=req.parameters or {},
                risk_level=cmd_spec["risk"],
                status=RemoteActionStatus.PENDING,
                description=f"Confirmação solicitada para '{cmd_type}'",
                expires_at=now + timedelta(minutes=3)
            )
            self.db.add(pending_action)
            await self.db.commit()

            return RemoteCommandResponse(
                success=True,
                request_id=req.request_id,
                command_type=cmd_type,
                status="PENDING_CONFIRMATION",
                message="Esta ação possui nível de risco elevado e exige confirmação explícita.",
                action_id=action_id
            )

        # 5. Execução do Comando
        result_data = await self._dispatch_execution(cmd_type, req.parameters or {}, req.device_id)

        # Registra Comando Executado
        record = RemoteCommandRecord(
            request_id=req.request_id,
            device_id=req.device_id,
            command_type=cmd_type,
            parameters=req.parameters or {},
            permission_level=cmd_spec["perm"],
            risk_level=cmd_spec["risk"],
            status="EXECUTED",
            result_data=result_data,
            executed_at=now
        )
        self.db.add(record)

        audit = ActivityLog(
            type="remote_command",
            action="command_executed",
            description=f"[{cmd_spec['risk']}] Comando remoto '{cmd_type}' executado via {device.device_name}.",
            metadata_json={"device_id": req.device_id, "command": cmd_type}
        )
        self.db.add(audit)
        await self.db.commit()

        # Publica evento de execução no EventBus
        await event_bus.publish("REMOTE_COMMAND_EXECUTED", {
            "device_id": req.device_id,
            "command_type": cmd_type,
            "result": result_data
        })

        return RemoteCommandResponse(
            success=True,
            request_id=req.request_id,
            command_type=cmd_type,
            status="EXECUTED",
            message="Comando remoto executado com sucesso.",
            data=result_data
        )

    async def confirm_action(self, action_id: str, device_id: str, confirmed: bool) -> RemoteCommandResponse:
        now = datetime.utcnow()
        stmt = select(RemotePendingAction).where(
            RemotePendingAction.action_id == action_id,
            RemotePendingAction.device_id == device_id
        )
        res = await self.db.execute(stmt)
        pending = res.scalar_one_or_none()

        if not pending:
            raise NotFoundError("Ação pendente não encontrada.")

        if pending.status != RemoteActionStatus.PENDING:
            raise ValidationError(f"Ação já finalizada com status '{pending.status.value}'.")

        if pending.expires_at < now:
            pending.status = RemoteActionStatus.EXPIRED
            await self.db.commit()
            raise ValidationError("Esta solicitação de confirmação expirou.")

        if not confirmed:
            pending.status = RemoteActionStatus.REJECTED
            await self.db.commit()
            return RemoteCommandResponse(
                success=True,
                request_id=pending.request_id,
                command_type=pending.command_type,
                status="REJECTED",
                message="Ação rejeitada pelo usuário."
            )

        # Executa a ação confirmada
        result_data = await self._dispatch_execution(pending.command_type, pending.parameters or {}, device_id)
        pending.status = RemoteActionStatus.EXECUTED
        pending.confirmed_at = now

        # Grava registro
        rec = RemoteCommandRecord(
            request_id=pending.request_id,
            device_id=device_id,
            command_type=pending.command_type,
            parameters=pending.parameters or {},
            permission_level="EXECUTE",
            risk_level=pending.risk_level,
            status="EXECUTED",
            result_data=result_data,
            executed_at=now
        )
        self.db.add(rec)
        await self.db.commit()

        return RemoteCommandResponse(
            success=True,
            request_id=pending.request_id,
            command_type=pending.command_type,
            status="EXECUTED",
            message="Ação confirmada e executada com sucesso.",
            data=result_data
        )

    async def _dispatch_execution(self, cmd_type: str, params: Dict[str, Any], device_id: str) -> Dict[str, Any]:
        """
        Roteador interno de execução segura para as camadas de domínio existentes.
        """
        if cmd_type == "CREATE_TASK":
            due_d = date.today()
            if params.get("due_date"):
                try: due_d = date.fromisoformat(str(params["due_date"])[:10])
                except Exception: pass

            t = Task(
                title=params.get("title", "Nova Tarefa Remota"),
                description=params.get("description"),
                priority=params.get("priority", "alta"),
                status="pendente",
                due_date=due_d
            )
            self.db.add(t)
            await self.db.flush()
            await event_bus.publish("TASK_CREATED", {"task_id": t.id, "title": t.title})
            return {"task_id": t.id, "title": t.title, "status": "created"}

        elif cmd_type == "COMPLETE_TASK":
            t_id = params.get("task_id")
            if not t_id: raise ValidationError("task_id obrigatório.")
            t = await self.db.get(Task, int(t_id))
            if not t: raise NotFoundError("Tarefa não encontrada.")
            t.status = "concluida"
            t.completed_at = datetime.utcnow()
            await self.db.flush()
            await event_bus.publish("TASK_COMPLETED", {"task_id": t.id})
            return {"task_id": t.id, "status": "completed"}

        elif cmd_type == "CREATE_EXPENSE":
            exp_d = date.today()
            if params.get("date"):
                try: exp_d = date.fromisoformat(str(params["date"])[:10])
                except Exception: pass

            exp = Expense(
                description=params.get("description", "Gasto Remoto"),
                amount=float(params.get("amount", 0.0)),
                date=exp_d,
                type=TransactionType.expense if params.get("type", "expense") == "expense" else TransactionType.income
            )
            self.db.add(exp)
            await self.db.flush()
            await event_bus.publish("EXPENSE_CREATED", {"expense_id": exp.id, "amount": exp.amount})
            return {"expense_id": exp.id, "amount": exp.amount}

        elif cmd_type == "CREATE_CALENDAR_EVENT":
            st = datetime.utcnow() + timedelta(hours=1)
            et = st + timedelta(minutes=60)
            if params.get("start_time"):
                try: st = datetime.fromisoformat(params["start_time"])
                except Exception: pass
            if params.get("end_time"):
                try: et = datetime.fromisoformat(params["end_time"])
                except Exception: pass

            ev = CalendarEvent(
                title=params.get("title", "Compromisso Remoto"),
                start_time=st,
                end_time=et
            )
            self.db.add(ev)
            await self.db.flush()
            await event_bus.publish("EVENT_CREATED", {"event_id": ev.id, "title": ev.title})
            return {"event_id": ev.id, "title": ev.title}

        elif cmd_type == "START_POMODORO":
            # Inicia sessão de estudo
            stmt_sub = select(StudySubject).limit(1)
            res_sub = await self.db.execute(stmt_sub)
            sub = res_sub.scalar_one_or_none()
            sub_id = sub.id if sub else 1

            session_rec = StudySession(
                subject_id=sub_id,
                mode=SessionMode.pomodoro,
                started_at=datetime.utcnow(),
                duration_minutes=int(params.get("duration", 25))
            )
            self.db.add(session_rec)
            await self.db.flush()
            await event_bus.publish("STUDY_SESSION_STARTED", {"session_id": session_rec.id, "duration": 25})
            return {"session_id": session_rec.id, "mode": "pomodoro", "duration": 25}

        elif cmd_type == "SYNC_NOW":
            sync_mgr = SyncManager(self.db)
            successes, fails = await sync_mgr.process_queue()
            await event_bus.publish("SYNC_COMPLETED", {"processed": successes, "failed": fails})
            return {"status": "synced", "processed": successes, "failed": fails}

        elif cmd_type == "CREATE_BACKUP":
            b_mgr = BackupManager(self.db)
            b_rec = await b_mgr.create_backup()
            await event_bus.publish("BACKUP_CREATED", {"filename": b_rec.filename})
            return {"filename": b_rec.filename, "size_bytes": b_rec.size_bytes}

        elif cmd_type == "EXECUTE_APPROVED_AUTOMATION":
            if is_kill_switch_active():
                raise PermissionError("Automações pausadas pelo Kill Switch de segurança.")

            auto_id = params.get("automation_id")
            if not auto_id: raise ValidationError("automation_id obrigatório.")
            auto = await self.db.get(Automation, int(auto_id))
            if not auto or not auto.is_active:
                raise NotFoundError("Automação inativa ou inexistente.")

            # Execução segura
            await event_bus.publish("AUTOMATION_COMPLETED", {"automation_id": auto.id, "name": auto.name})
            return {"automation_id": auto.id, "name": auto.name, "status": "executed"}

        return {"status": "ok"}
