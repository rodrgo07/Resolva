from typing import Dict, Any
from app.ai.tools.base import BaseTool
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate

class ListTasksTool(BaseTool):
    name = "list_tasks"
    description = "Lista tarefas pendentes ou com status específico no Resolva."
    parameters = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["pendente", "em_andamento", "concluida", "all"],
                "description": "Filtro de status das tarefas."
            }
        }
    }
    permission_level = "READ"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        if not db:
            return {"error": "Database session not available"}
        repo = TaskRepository(db)
        status_filter = args.get("status", "pendente")
        if status_filter == "all":
            tasks = await repo.get_all(0, 50)
        else:
            tasks = await repo.get_pending()
        
        return {
            "total": len(tasks),
            "tasks": [{"id": t.id, "title": t.title, "priority": t.priority, "status": t.status, "due_date": str(t.due_date)} for t in tasks]
        }

class CreateTaskTool(BaseTool):
    name = "create_task"
    description = "Cria uma nova tarefa no Resolva com título, prioridade e categoria."
    parameters = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Título da tarefa a ser criada"},
            "priority": {"type": "string", "enum": ["baixa", "media", "alta", "urgente"], "description": "Nível de prioridade"},
            "category": {"type": "string", "description": "Categoria da tarefa (ex: Estudos, Trabalho, Pessoal)"}
        },
        "required": ["title"]
    }
    permission_level = "WRITE"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        if not db:
            return {"error": "Database session not available"}
        repo = TaskRepository(db)
        created = await repo.create(
            title=args["title"],
            priority=args.get("priority", "media"),
            category=args.get("category"),
            status="pendente"
        )
        return {
            "success": True,
            "task_id": created.id,
            "title": created.title,
            "status": "pendente"
        }
