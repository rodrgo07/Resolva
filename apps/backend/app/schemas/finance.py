from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from app.models.finance import CategoryType, TransactionType, BudgetPeriod

class CategoryCreate(BaseModel):
    name: str
    color: Optional[str] = None
    icon: Optional[str] = None
    type: CategoryType

class CategoryResponse(BaseModel):
    id: int
    name: str
    color: Optional[str]
    icon: Optional[str]
    type: CategoryType
    
    model_config = ConfigDict(from_attributes=True)

class TransactionCreate(BaseModel):
    amount: float
    description: str
    category_id: Optional[int] = None
    date: date
    type: TransactionType
    recurrence: Optional[str] = None
    notes: Optional[str] = None

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    date: Optional[date] = None
    type: Optional[TransactionType] = None
    recurrence: Optional[str] = None
    notes: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    amount: float
    description: str
    category_id: Optional[int]
    category: Optional[CategoryResponse]
    date: date
    type: TransactionType
    recurrence: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class BudgetCreate(BaseModel):
    category_id: int
    limit_amount: float
    period: BudgetPeriod
    year: Optional[int] = None
    month: Optional[int] = None

class BudgetResponse(BaseModel):
    id: int
    category_id: int
    limit_amount: float
    period: BudgetPeriod
    year: Optional[int]
    month: Optional[int]
    
    model_config = ConfigDict(from_attributes=True)

class FinanceSummary(BaseModel):
    total_income: float
    total_expense: float
    balance: float

class CategoryBreakdown(BaseModel):
    category_name: str
    total_amount: float
    percentage: float
