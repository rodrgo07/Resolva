from typing import Dict, Any, List, Optional
from datetime import datetime, date
from sqlalchemy import select, and_

from app.ai.tools.base import BaseTool
from app.ai.permissions import PermissionLevel, RiskLevel
from app.ai.context_engine import ContextEngine
from app.ai.planner import PlanningEngine
from app.models.task import Task, Subtask, TaskPriority, TaskStatus
from app.models.calendar import CalendarEvent
from app.models.finance import Expense, TransactionType
from app.models.study import StudySession, StudySubject, SessionMode
from app.models.automation import Automation
from app.repositories.task_repository import TaskRepository
from app.repositories.email_repository import EmailRepository

# ==========================================
# 1. TOOLS DE LEITURA & CONTEXTO
# ==========================================

class GetTodayContextTool(BaseTool):
    name = "get_today_context"
    description = "Retorna uma visão geral e estruturada do dia: hora atual, tarefas atrasadas, compromissos, e-mails urgentes e notificações."
    parameters = {"type": "object", "properties": {}}
    permission_level = PermissionLevel.READ
    risk_level = RiskLevel.LOW
    category = "context"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        if not db:
            return {"error": "Banco de dados indisponível"}
        engine = ContextEngine(db)
        return await engine.get_current_context()

class OrganizeDayTool(BaseTool):
    name = "organize_my_day"
    description = "Planeja e organiza o dia do usuário dividindo afazeres em prioridades (alta/média), blocos de tempo e sugestões com base na agenda."
    parameters = {"type": "object", "properties": {}}
    permission_level = PermissionLevel.SUGGEST
    risk_level = RiskLevel.LOW
    category = "planner"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        if not db:
            return {"error": "Banco de dados indisponível"}
        planner = PlanningEngine(ContextEngine(db))
        return await planner.generate_daily_plan()

class GetOverdueTasksTool(BaseTool):
    name = "get_overdue_tasks"
    description = "Retorna exclusivamente a lista de tarefas pendentes que já ultrapassaram o prazo de vencimento."
    parameters = {"type": "object", "properties": {}}
    permission_level = PermissionLevel.READ
    risk_level = RiskLevel.LOW
    category = "tasks"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        today = date.today()
        stmt = select(Task).where(and_(Task.status.in_([TaskStatus.pendente, TaskStatus.em_andamento]), Task.due_date < today))
        res = await db.execute(stmt)
        tasks = res.scalars().all()
        return {
            "total_overdue": len(tasks),
            "tasks": [{"id": t.id, "title": t.title, "priority": str(t.priority), "due_date": str(t.due_date)} for t in tasks]
        }

class GetUpcomingEventsTool(BaseTool):
    name = "get_upcoming_events"
    description = "Lista compromissos e eventos futuros cadastrados no calendário do Resolva."
    parameters = {
        "type": "object",
        "properties": {
            "days_ahead": {"type": "integer", "description": "Quantos dias à frente buscar", "default": 3}
        }
    }
    permission_level = PermissionLevel.READ
    risk_level = RiskLevel.LOW
    category = "calendar"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        days = args.get("days_ahead", 3)
        stmt = select(CalendarEvent).order_by(CalendarEvent.start_time.asc()).limit(15)
        res = await db.execute(stmt)
        events = res.scalars().all()
        return {
            "total": len(events),
            "events": [{"id": e.id, "title": e.title, "start_time": str(e.start_time), "type": str(e.type)} for e in events]
        }

# ==========================================
# 2. TOOLS DE TAREFAS & ESCRITA
# ==========================================

class CompleteTaskTool(BaseTool):
    name = "complete_task"
    description = "Marca uma tarefa como concluída no Resolva pelo ID. Requer confirmação."
    parameters = {
        "type": "object",
        "properties": {
            "task_id": {"type": "integer", "description": "ID da tarefa a concluir"}
        },
        "required": ["task_id"]
    }
    permission_level = PermissionLevel.WRITE
    risk_level = RiskLevel.MEDIUM
    requires_confirmation = True
    confirmation_message = "Deseja marcar esta tarefa como concluída?"
    category = "tasks"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        task_id = args["task_id"]
        stmt = select(Task).where(Task.id == task_id)
        res = await db.execute(stmt)
        task = res.scalars().first()
        if not task:
            return {"error": f"Tarefa {task_id} não encontrada"}
        task.status = TaskStatus.concluida
        task.completed_at = datetime.now()
        await db.commit()
        return {"success": True, "message": f"Tarefa '{task.title}' marcada como concluída."}

class DeleteTaskTool(BaseTool):
    name = "delete_task"
    description = "Exclui permanentemente uma tarefa. Requer confirmação explícita."
    parameters = {
        "type": "object",
        "properties": {
            "task_id": {"type": "integer", "description": "ID da tarefa a excluir"}
        },
        "required": ["task_id"]
    }
    permission_level = PermissionLevel.WRITE
    risk_level = RiskLevel.HIGH
    requires_confirmation = True
    confirmation_message = "Tem certeza que deseja excluir esta tarefa permanentemente?"
    category = "tasks"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        task_id = args["task_id"]
        stmt = select(Task).where(Task.id == task_id)
        res = await db.execute(stmt)
        task = res.scalars().first()
        if not task:
            return {"error": f"Tarefa {task_id} não encontrada"}
        await db.delete(task)
        await db.commit()
        return {"success": True, "message": f"Tarefa {task_id} excluída com sucesso."}

# ==========================================
# 3. TOOLS DE AGENDA & CALENDÁRIO
# ==========================================

class CreateCalendarEventTool(BaseTool):
    name = "create_calendar_event"
    description = "Cria um novo evento ou compromisso no calendário. Requer confirmação."
    parameters = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Título do evento"},
            "start_time": {"type": "string", "description": "Data e hora de início (ISO 8601, ex: 2026-08-30T14:00:00)"},
            "end_time": {"type": "string", "description": "Data e hora de fim (ISO 8601, ex: 2026-08-30T15:00:00)"},
            "description": {"type": "string", "description": "Descrição opcional"}
        },
        "required": ["title", "start_time", "end_time"]
    }
    permission_level = PermissionLevel.WRITE
    risk_level = RiskLevel.MEDIUM
    requires_confirmation = True
    confirmation_message = "Deseja agendar este novo evento?"
    category = "calendar"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        try:
            start_dt = datetime.fromisoformat(args["start_time"])
            end_dt = datetime.fromisoformat(args["end_time"])
        except Exception:
            start_dt = datetime.now()
            end_dt = datetime.now()

        event = CalendarEvent(
            title=args["title"],
            description=args.get("description"),
            start_time=start_dt,
            end_time=end_dt,
            all_day=False,
            type="appointment",
            source="local"
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return {"success": True, "event_id": event.id, "title": event.title}

# ==========================================
# 4. TOOLS DE ESTUDO & POMODORO
# ==========================================

class CreateStudySessionTool(BaseTool):
    name = "create_study_session"
    description = "Registra uma nova sessão de estudos realizada no Resolva."
    parameters = {
        "type": "object",
        "properties": {
            "subject_name": {"type": "string", "description": "Nome da matéria ou disciplina"},
            "duration_minutes": {"type": "integer", "description": "Duração em minutos", "default": 25},
            "notes": {"type": "string", "description": "Anotações da sessão"}
        },
        "required": ["subject_name"]
    }
    permission_level = PermissionLevel.WRITE
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    category = "studies"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        subj_stmt = select(StudySubject).where(StudySubject.name.ilike(f"%{args['subject_name']}%"))
        res = await db.execute(subj_stmt)
        subject = res.scalars().first()
        if not subject:
            subject = StudySubject(name=args["subject_name"], description="Criada via Resolva Agent")
            db.add(subject)
            await db.commit()
            await db.refresh(subject)

        duration = args.get("duration_minutes", 25)
        session = StudySession(
            subject_id=subject.id,
            mode=SessionMode.pomodoro if duration <= 30 else SessionMode.free,
            started_at=datetime.now(),
            duration_minutes=duration,
            notes=args.get("notes")
        )
        db.add(session)
        await db.commit()
        return {"success": True, "subject": subject.name, "duration_minutes": duration}

# ==========================================
# 5. TOOLS DE AUTOMAÇÃO
# ==========================================

class ListAutomationsTool(BaseTool):
    name = "list_automations"
    description = "Lista automações de sistema cadastradas no Resolva (ex: Modo Programação, Limpeza de Ambiente)."
    parameters = {"type": "object", "properties": {}}
    permission_level = PermissionLevel.READ
    risk_level = RiskLevel.LOW
    category = "automation"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        stmt = select(Automation).where(Automation.is_active == True)
        res = await db.execute(stmt)
        autos = res.scalars().all()
        return {
            "total": len(autos),
            "automations": [{"id": a.id, "name": a.name, "description": a.description} for a in autos]
        }

class ExecuteAutomationTool(BaseTool):
    name = "execute_automation"
    description = "Executa uma automação existente por ID. Ação de ALTO RISCO: NUNCA executa comandos arbitrários, apenas rotinas registradas na whitelist."
    parameters = {
        "type": "object",
        "properties": {
            "automation_id": {"type": "integer", "description": "ID da automação"}
        },
        "required": ["automation_id"]
    }
    permission_level = PermissionLevel.EXECUTE
    risk_level = RiskLevel.HIGH
    requires_confirmation = True
    confirmation_message = "Confirma a execução desta automação do sistema?"
    category = "automation"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        from app.automation.engine import AutomationEngine
        db = services.get("db")
        engine = AutomationEngine(db)
        res = await engine.run_automation(args["automation_id"], is_confirmed=True)
        return {"id": res.id, "status": res.status, "log": res.log}

# ==========================================
# 6. TOOLS NATIVAS DO WINDOWS (FASE 26)
# ==========================================

class GetSystemStatusTool(BaseTool):
    name = "get_system_status"
    description = "Retorna o status atual do sistema Resolva no Windows: conectividade, sincronização, kill switch de automações e hora do sistema."
    parameters = {"type": "object", "properties": {}}
    permission_level = PermissionLevel.READ
    risk_level = RiskLevel.LOW
    category = "windows"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        from app.automation.kill_switch import is_kill_switch_active
        return {
            "status": "online",
            "automations_kill_switch": is_kill_switch_active(),
            "timestamp": datetime.now().isoformat(),
            "os": "windows"
        }

class OpenAllowedApplicationTool(BaseTool):
    name = "open_allowed_application"
    description = "Abre um aplicativo seguro do Windows previamente registrado na whitelist (ex: vscode, chrome, edge, spotify, notepad, calc). Requer confirmação."
    parameters = {
        "type": "object",
        "properties": {
            "app_name": {"type": "string", "description": "Nome do aplicativo autorizado (ex: vscode, chrome, spotify, notepad, calc)"}
        },
        "required": ["app_name"]
    }
    permission_level = PermissionLevel.EXECUTE
    risk_level = RiskLevel.HIGH
    requires_confirmation = True
    confirmation_message = "Confirma a abertura do aplicativo Windows solicitado?"
    category = "windows"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        from app.automation.security import ALLOWED_WINDOWS_APPS
        import subprocess
        app_name = args.get("app_name", "").lower().strip()
        if app_name not in ALLOWED_WINDOWS_APPS:
            return {"error": f"Aplicativo '{app_name}' não permitido na whitelist de segurança."}
        try:
            subprocess.Popen(app_name, shell=False)
            return {"success": True, "message": f"Aplicativo '{app_name}' aberto com sucesso."}
        except Exception as e:
            return {"success": False, "message": f"Não foi possível abrir '{app_name}': {str(e)}"}

class ShowNotificationTool(BaseTool):
    name = "show_notification"
    description = "Exibe uma notificação nativa para o usuário no Windows e registra na central de notificações."
    parameters = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Título da notificação"},
            "message": {"type": "string", "description": "Conteúdo da mensagem"},
            "type": {"type": "string", "description": "Categoria (task, calendar, system, etc)", "default": "system"}
        },
        "required": ["title", "message"]
    }
    permission_level = PermissionLevel.EXECUTE
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    category = "windows"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        from app.models.notification import Notification
        db = services.get("db")
        notif = Notification(
            title=args["title"],
            message=args["message"],
            type=args.get("type", "system"),
            is_read=False
        )
        if db:
            db.add(notif)
            await db.commit()
        return {"success": True, "title": args["title"], "message": args["message"]}

class FocusResolvaTool(BaseTool):
    name = "focus_resolva"
    description = "Restaura e traz a janela do Resolva para frente no Windows."
    parameters = {"type": "object", "properties": {}}
    permission_level = PermissionLevel.READ
    risk_level = RiskLevel.LOW
    category = "windows"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "action": "focus_resolva", "message": "Janela do Resolva restaurada para o primeiro plano."}

class OpenCommandPaletteTool(BaseTool):
    name = "open_command_palette"
    description = "Abre a interface do Command Palette global do Resolva."
    parameters = {"type": "object", "properties": {}}
    permission_level = PermissionLevel.READ
    risk_level = RiskLevel.LOW
    category = "windows"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "action": "open_command_palette", "message": "Command Palette aberta com sucesso."}
