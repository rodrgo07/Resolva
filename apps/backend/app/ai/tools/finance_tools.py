from typing import Dict, Any
from datetime import date, timedelta
from app.ai.tools.base import BaseTool
from app.repositories.finance_repository import FinanceRepository

class GetFinanceSummaryTool(BaseTool):
    name = "get_finance_summary"
    description = "Retorna o resumo financeiro atual com total de receitas, despesas e saldo líquido."
    parameters = {
        "type": "object",
        "properties": {
            "days": {"type": "integer", "description": "Período em dias para o resumo (padrão 30 dias)"}
        }
    }
    permission_level = "READ"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        if not db:
            return {"error": "Database session not available"}
        repo = FinanceRepository(db)
        days = args.get("days", 30)
        start_date = date.today() - timedelta(days=days)
        end_date = date.today()
        summary = await repo.get_summary(start_date, end_date)
        return summary

class CreateExpenseTool(BaseTool):
    name = "create_expense"
    description = "Registra uma nova despesa ou gasto no Resolva."
    parameters = {
        "type": "object",
        "properties": {
            "amount": {"type": "number", "description": "Valor monetário do gasto em Reais (ex: 45.50)"},
            "description": {"type": "string", "description": "Descrição do gasto (ex: Almoço, Uber)"},
            "category_id": {"type": "integer", "description": "ID opcional da categoria"}
        },
        "required": ["amount", "description"]
    }
    permission_level = "WRITE"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        if not db:
            return {"error": "Database session not available"}
        repo = FinanceRepository(db)
        created = await repo.create(
            amount=float(args["amount"]),
            description=args["description"],
            category_id=args.get("category_id"),
            date=date.today(),
            type="expense"
        )
        return {
            "success": True,
            "id": created.id,
            "amount": created.amount,
            "description": created.description
        }
