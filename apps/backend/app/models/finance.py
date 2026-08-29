from datetime import date
from typing import Optional
from sqlalchemy import String, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from .base import BaseModel

class CategoryType(str, enum.Enum):
    task = "task"
    finance = "finance"
    study = "study"
    email = "email"

class TransactionType(str, enum.Enum):
    expense = "expense"
    income = "income"
    
class BudgetPeriod(str, enum.Enum):
    weekly = "weekly"
    monthly = "monthly"

class Category(BaseModel):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100))
    color: Mapped[Optional[str]] = mapped_column(String(50))
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    type: Mapped[CategoryType] = mapped_column(SQLEnum(CategoryType))
    
    expenses: Mapped[list["Expense"]] = relationship(back_populates="category")
    budgets: Mapped[list["Budget"]] = relationship(back_populates="category")

class Expense(BaseModel):
    __tablename__ = "expenses"

    amount: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(String(255))
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))
    date: Mapped[date] = mapped_column()
    type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType))
    recurrence: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(String)
    
    category: Mapped[Optional["Category"]] = relationship(back_populates="expenses")

class Budget(BaseModel):
    __tablename__ = "budgets"

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    limit_amount: Mapped[float] = mapped_column(Float)
    period: Mapped[BudgetPeriod] = mapped_column(SQLEnum(BudgetPeriod))
    year: Mapped[Optional[int]] = mapped_column()
    month: Mapped[Optional[int]] = mapped_column()
    
    category: Mapped["Category"] = relationship(back_populates="budgets")
