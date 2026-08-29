from fastapi import APIRouter, Depends, Query, status
from typing import List
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.finance import (
    TransactionCreate, TransactionUpdate, TransactionResponse, 
    FinanceSummary, CategoryBreakdown, BudgetResponse, CategoryResponse
)
from app.services.finance_service import FinanceService
from app.repositories.finance_repository import FinanceRepository

router = APIRouter()

def get_finance_service(db: AsyncSession = Depends(get_db)) -> FinanceService:
    repo = FinanceRepository(db)
    return FinanceService(repo)

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(skip: int = 0, limit: int = 100, service: FinanceService = Depends(get_finance_service)):
    return await service.get_all_transactions(skip, limit)

@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction: TransactionCreate, service: FinanceService = Depends(get_finance_service)):
    return await service.create_transaction(transaction)

@router.get("/transactions/{id}", response_model=TransactionResponse)
async def get_transaction(id: int, service: FinanceService = Depends(get_finance_service)):
    return await service.get_transaction(id)

@router.put("/transactions/{id}", response_model=TransactionResponse)
async def update_transaction(id: int, transaction: TransactionUpdate, service: FinanceService = Depends(get_finance_service)):
    return await service.update_transaction(id, transaction)

@router.delete("/transactions/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(id: int, service: FinanceService = Depends(get_finance_service)):
    await service.delete_transaction(id)
    return None

@router.get("/summary", response_model=FinanceSummary)
async def get_summary(
    start_date: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    end_date: date = Query(default_factory=lambda: date.today()),
    service: FinanceService = Depends(get_finance_service)
):
    return await service.get_summary(start_date, end_date)

@router.get("/categories/breakdown", response_model=List[CategoryBreakdown])
async def get_category_breakdown(
    start_date: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    end_date: date = Query(default_factory=lambda: date.today()),
    service: FinanceService = Depends(get_finance_service)
):
    return await service.get_category_breakdown(start_date, end_date)

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(service: FinanceService = Depends(get_finance_service)):
    return await service.get_categories()

@router.get("/budgets", response_model=List[BudgetResponse])
async def get_budgets(service: FinanceService = Depends(get_finance_service)):
    return await service.get_budgets()
