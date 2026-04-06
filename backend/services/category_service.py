from sqlalchemy.ext.asyncio import AsyncSession
from models.category import Category, CashflowTypeEnum
from fastapi import HTTPException, status
from sqlalchemy import select
from typing import List

async def create_category(
    db: AsyncSession,
    *,
    name: str,
    type: CashflowTypeEnum,
) -> Category:
    existing_category = (await db.execute(select(Category).where(Category.name == name))).scalar_one_or_none()
    if existing_category is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category with this name already exists")

    category_db = Category(name=name, type=type)
    db.add(category_db)
    await db.commit()
    await db.refresh(category_db)
    return category_db

async def list_categories(db: AsyncSession) -> List[Category]:

    result = await db.execute(select(Category).order_by(Category.created_at.desc()))
    return list(result.scalars().all())