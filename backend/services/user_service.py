from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserResponseSchema
from models.auth import User, UserRole
from sqlalchemy import select
from fastapi import HTTPException,status
import bcrypt # type: ignore
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

async def create_user(
    db: AsyncSession,
    *,
    name: str,
    email: str,
    password: str,
    role: UserRole) -> User:

    if role == UserRole.admin:
        existing_admin_count = (await db.execute(
            select(User).where(User.role == UserRole.admin, User.is_active == True)
        )).scalar_one_or_none()
        if existing_admin_count is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot create another admin. There can be only one admin.")

    existing = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    user_db = User(name=name, email=email, hashed_password=hashed_pw, role=role, is_active=True)
    db.add(user_db)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
    await db.refresh(user_db)
    return user_db

    


async def list_users(db: AsyncSession, *, skip: int, limit: int) -> List[User]:
 
    stmt = select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_user(db: AsyncSession, *, user_id: UUID) -> User:
    user_db = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_db

async def update_user(
    db: AsyncSession,
    *,
    admin_user: User,
    user_id: UUID,
    name: Optional[str],
    role: Optional[UserRole],
    is_active: Optional[bool],
) -> User:
    
    user_db = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if is_active is False and admin_user.role == UserRole.admin and admin_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin cannot deactivate themselves")

    if role is not None and role == UserRole.admin and user_db.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot promote user to admin. There can be only one admin.",
        )

    if role is not None and user_db.role == UserRole.admin and role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot demote admin to another role. There must be one admin.",
        )

    if name is not None:
        user_db.name = name
    if role is not None:
        user_db.role = role
    if is_active is not None:
        user_db.is_active = is_active

    await db.commit()
    await db.refresh(user_db)
    return user_db

async def delete_user(db: AsyncSession, *, admin_user: User, user_id: UUID) -> User:
    user_db = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if admin_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin cannot delete themselves")
    
    if user_db.role == UserRole.admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete admin users")
    
    await db.delete(user_db)
    await db.commit()

    return user_db