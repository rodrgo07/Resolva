from typing import Dict, Any
from app.ai.tools.base import BaseTool
from app.repositories.study_repository import StudyRepository

class GetStudySummaryTool(BaseTool):
    name = "get_study_summary"
    description = "Retorna o total de horas e minutos estudados hoje, nesta semana e no mês."
    parameters = {"type": "object", "properties": {}}
    permission_level = "READ"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        if not db:
            return {"error": "Database session not available"}
        repo = StudyRepository(db)
        return await repo.get_study_summary()
