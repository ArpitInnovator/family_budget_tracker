from pydantic import BaseModel
from decimal import Decimal
from models.category import CashflowTypeEnum
from typing import List
from datetime import date

class DashboardSummaryResponseSchema(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal

class CategoryTotalsItemSchema(BaseModel):
    category_name: str
    type: CashflowTypeEnum
    total_amount: Decimal

class DashboardCategoryTotalsResponseSchema(BaseModel):
    items: List[CategoryTotalsItemSchema]

class RecentActivityItemSchema(BaseModel):
    id: str
    user_id: str
    user_name: str
    category_id: str
    category_name: str
    amount: Decimal
    type: CashflowTypeEnum
    date: date
    notes: str | None = None


class DashboardRecentActivityResponseSchema(BaseModel):
    items: List[RecentActivityItemSchema]
