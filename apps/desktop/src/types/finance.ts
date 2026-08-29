// Finance types matching backend schema

export type TransactionType = "expense" | "income";

export interface Transaction {
  id: number;
  amount: number;
  description: string;
  category_id: number | null;
  category_name: string | null;
  date: string;
  type: TransactionType;
  recurrence: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  amount: number;
  description: string;
  category_id?: number;
  date?: string;
  type: TransactionType;
  recurrence?: string;
  notes?: string;
}

export interface TransactionUpdate {
  amount?: number;
  description?: string;
  category_id?: number;
  date?: string;
  type?: TransactionType;
  notes?: string;
}

export interface FinanceSummary {
  total_income: number;
  total_expenses: number;
  balance: number;
  week_expenses: number;
  month_expenses: number;
  previous_week_expenses: number;
  previous_month_expenses: number;
}

export interface CategoryBreakdown {
  category: string;
  amount: number;
  percentage: number;
  color: string;
}

export interface Category {
  id: number;
  name: string;
  color: string;
  icon: string;
  type: string;
  created_at: string;
}

export interface CategoryCreate {
  name: string;
  color: string;
  icon?: string;
  type: string;
}

export interface Budget {
  id: number;
  category_id: number;
  category_name: string;
  limit_amount: number;
  spent: number;
  remaining: number;
  period: string;
  year: number;
  month: number;
}

export interface BudgetCreate {
  category_id: number;
  limit_amount: number;
  period: string;
  year: number;
  month: number;
}
