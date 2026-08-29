from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date

from app.models.finance import Expense, Budget, TransactionType, Category
from app.repositories.base import BaseRepository

class FinanceRepository(BaseRepository[Expense]):
    def __init__(self, db: AsyncSession):
        super().__init__(Expense, db)

    async def get_by_date_range(self, start_date: date, end_date: date) -> List[Expense]:
        query = select(Expense).where(and_(Expense.date >= start_date, Expense.date <= end_date))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_type(self, type: TransactionType) -> List[Expense]:
        query = select(Expense).where(Expense.type == type)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_summary(self, start_date: date, end_date: date) -> Dict[str, float]:
        query = select(
            Expense.type, 
            func.sum(Expense.amount)
        ).where(
            and_(Expense.date >= start_date, Expense.date <= end_date)
        ).group_by(Expense.type)
        
        result = await self.db.execute(query)
        
        total_income = 0.0
        total_expense = 0.0
        
        for type_, total in result.all():
            if type_ == TransactionType.income:
                total_income = total or 0.0
            else:
                total_expense = total or 0.0
                
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense
        }

    async def get_category_breakdown(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        query = select(
            Category.name, 
            func.sum(Expense.amount)
        ).join(Expense, Expense.category_id == Category.id).where(
            and_(
                Expense.type == TransactionType.expense,
                Expense.date >= start_date, 
                Expense.date <= end_date
            )
        ).group_by(Category.name)
        
        result = await self.db.execute(query)
        
        breakdown = []
        total_expense = sum([row[1] for row in result.all()])
        
        # re-execute or reuse result. Using a new query for simplicity as result.all() consumed the iterator
        result = await self.db.execute(query)
        
        for cat_name, total in result.all():
            breakdown.append({
                "category_name": cat_name,
                "total_amount": total or 0.0,
                "percentage": (total / total_expense * 100) if total_expense > 0 else 0
            })
            
        return breakdown

    async def get_budgets(self) -> List[Budget]:
        query = select(Budget)
        result = await self.db.execute(query)
        return list(result.scalars().all())
