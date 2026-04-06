from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException,status
from models.category import Category, CashflowTypeEnum
from models.transaction import Transaction
from datetime import date
from decimal import Decimal
from typing import Optional
from models.auth import User
from typing import List
from sqlalchemy import and_, BinaryExpression

async def _get_category(db: AsyncSession, *, category_id: UUID) -> Category:
   
    category = (await db.execute(select(Category).where(Category.id == category_id))).scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category

async def _get_transaction(db: AsyncSession, *, transaction_id: UUID) -> Transaction:
    txn = (
        await db.execute(select(Transaction).where(Transaction.id == transaction_id, Transaction.is_deleted.is_(False)))
    ).scalar_one_or_none()
    if txn is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return txn

async def create_transaction(
    db: AsyncSession,
    *,
    user_id: UUID,
    category_id: UUID,
    amount: Decimal,
    type: CashflowTypeEnum,
    txn_date: date,
    notes: Optional[str],
) -> Transaction:
   
    
    category = await _get_category(db, category_id=category_id)
    if category.type != type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transaction type must match category type")

    
    _user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if _user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    txn = Transaction(
        user_id=user_id,
        category_id=category_id,
        amount=amount,
        type=type,
        date=txn_date,
        notes=notes,
    )
    db.add(txn)
    await db.commit()
    await db.refresh(txn)
    return txn


async def list_transactions(
    db: AsyncSession,
    *,
    type: Optional[CashflowTypeEnum],
    category_id: Optional[UUID],
    start_date: Optional[date],
    end_date: Optional[date],
    search: Optional[str],
    skip: int,
    limit: int,
) -> List[Transaction]:

  if skip < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="skip must be >= 0")
  if limit < 1 or limit > 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="limit must be between 1 and 200")

  conditions: List[BinaryExpression] = [Transaction.is_deleted.is_(False)]
  if type is not None:
        conditions.append(Transaction.type == type)
  if category_id is not None:
        conditions.append(Transaction.category_id == category_id)
  if start_date is not None:
        conditions.append(Transaction.date >= start_date)
  if end_date is not None:
        conditions.append(Transaction.date <= end_date)
  if search:
       
        conditions.append(Transaction.notes.ilike(f"%{search}%"))

  stmt = (
        select(Transaction)
        .where(and_(*conditions))
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
  result = await db.execute(stmt)
  return list(result.scalars().all())
   
async def get_transaction(db: AsyncSession, *, transaction_id: UUID) -> Transaction:
    return await _get_transaction(db, transaction_id=transaction_id)

async def update_transaction(
    db: AsyncSession,
    *,
    _admin_user_id: UUID,
    transaction_id: UUID,
    user_id: Optional[UUID],
    category_id: Optional[UUID],
    amount: Optional[Decimal],
    type: Optional[CashflowTypeEnum],
    txn_date: Optional[date],
    notes: Optional[str],
) -> Transaction:
    
    txn = await _get_transaction(db, transaction_id=transaction_id)

    final_type = type if type is not None else txn.type
    final_category_id = category_id if category_id is not None else txn.category_id
    category = await _get_category(db, category_id=final_category_id)
    if category.type != final_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transaction type must match category type")

    if user_id is not None:
        user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        txn.user_id = user_id

    if category_id is not None:
        txn.category_id = category_id
    if type is not None:
        txn.type = type
    if amount is not None:
        txn.amount = amount
    if txn_date is not None:
        txn.date = txn_date
    if notes is not None:
        txn.notes = notes

    await db.commit()
    await db.refresh(txn)
    return txn


async def soft_delete_transaction(
    db: AsyncSession,
    *,
    _admin_user_id: UUID,
    transaction_id: UUID,
) -> Transaction:
    
    txn = await _get_transaction(db, transaction_id=transaction_id)
    txn.is_deleted = True
    await db.commit()
    await db.refresh(txn)
    return txn
