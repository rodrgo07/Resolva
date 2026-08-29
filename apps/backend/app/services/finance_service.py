from typing import List, Dict, Any
from datetime import date
from app.repositories.finance_repository import FinanceRepository
from app.schemas.finance import TransactionCreate, TransactionUpdate
from app.models.finance import Expense, TransactionType
from app.core.exceptions import NotFoundError

class FinanceService:
    def __init__(self, finance_repo: FinanceRepository):
        self.finance_repo = finance_repo

    async def get_all_transactions(self, skip: int = 0, limit: int = 100) -> List[Expense]:
        return await self.finance_repo.get_all(skip=skip, limit=limit)

    async def get_transaction(self, id: int) -> Expense:
        transaction = await self.finance_repo.get_by_id(id)
        if not transaction:
            raise NotFoundError(f"Transaction with ID {id} not found")
        return transaction

    async def create_transaction(self, data: TransactionCreate) -> Expense:
        return await self.finance_repo.create(**data.model_dump(exclude_unset=True))

    async def update_transaction(self, id: int, data: TransactionUpdate) -> Expense:
        await self.get_transaction(id)
        return await self.finance_repo.update(id, **data.model_dump(exclude_unset=True))

    async def delete_transaction(self, id: int) -> bool:
        await self.get_transaction(id)
        return await self.finance_repo.delete(id)

    async def get_summary(self, start_date: date, end_date: date) -> Dict[str, float]:
        return await self.finance_repo.get_summary(start_date, end_date)

    async def get_category_breakdown(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        return await self.finance_repo.get_category_breakdown(start_date, end_date)

    async def get_budgets(self):
        return await self.finance_repo.get_budgets()
