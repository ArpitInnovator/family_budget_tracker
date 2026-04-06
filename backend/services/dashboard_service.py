from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import text
from models.transaction import Transaction
from models.category import CashflowTypeEnum
from datetime import date
from decimal import Decimal
from typing import Dict, Tuple, List
from models.category import Category
from models.auth import User


def _validate_month_year(*, month: int, year: int) -> None:
   
    if month < 1 or month > 12:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="month must be between 1 and 12")
    if year < 1900 or year > 3000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="year is out of range")


def _month_range(month: int, year: int) -> Tuple[date, date]:
   
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)

    return start, end


async def summary(db: AsyncSession, *, month: int, year: int) -> Dict[str, Decimal]:
    
    _validate_month_year(month=month, year=year)
    start, end_exclusive = _month_range(month, year)

    total_income = func.coalesce(
        func.sum(
            case(
                (Transaction.type == CashflowTypeEnum.income, Transaction.amount),
                else_=0,
            )
        ),
        0,
    ).label("total_income")
    total_expenses = func.coalesce(
        func.sum(
            case(
                (Transaction.type == CashflowTypeEnum.expense, Transaction.amount),
                else_=0,
            )
        ),
        0,
    ).label("total_expenses")

    stmt = (
        select(total_income, total_expenses)
        .where(
            Transaction.is_deleted.is_(False),
            Transaction.date >= start,
            Transaction.date < end_exclusive,
        )
        .limit(1)
    )
    row = (await db.execute(stmt)).one()
    income: Decimal = row.total_income
    expenses: Decimal = row.total_expenses
    return {
        "total_income": income,
        "total_expenses": expenses,
        "net_balance": income - expenses,
    }

async def category_totals(db: AsyncSession, *, month: int, year: int) -> List[Dict[str, object]]:
  
    _validate_month_year(month=month, year=year)
    start, end_exclusive = _month_range(month, year)

    stmt = (
        select(
            Category.name.label("category_name"),
            Category.type.label("type"),
            func.coalesce(func.sum(Transaction.amount), 0).label("total_amount"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .where(
            Transaction.is_deleted.is_(False),
            Transaction.date >= start,
            Transaction.date < end_exclusive,
            Transaction.type == Category.type,
        )
        .group_by(Category.id)
        .order_by(Category.name.asc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {"category_name": r.category_name, "type": r.type, "total_amount": r.total_amount} for r in rows
    ]


async def recent_activity(db: AsyncSession) -> List[Dict[str, object]]:
    
    stmt = (
        select(
            Transaction.id.label("id"),
            Transaction.user_id.label("user_id"),
            User.name.label("user_name"),
            Transaction.category_id.label("category_id"),
            Category.name.label("category_name"),
            Transaction.amount.label("amount"),
            Transaction.type.label("type"),
            Transaction.date.label("date"),
            Transaction.notes.label("notes"),
        )
        .join(User, User.id == Transaction.user_id)
        .join(Category, Category.id == Transaction.category_id)
        .where(Transaction.is_deleted.is_(False))
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .limit(10)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "id": str(r.id),
            "user_id": str(r.user_id),
            "user_name": r.user_name,
            "category_id": str(r.category_id),
            "category_name": r.category_name,
            "amount": r.amount,
            "type": r.type,
            "date": r.date,
            "notes": r.notes,
        }
        for r in rows
    ]

