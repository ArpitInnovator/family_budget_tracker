from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.security import create_access_token
from schemas import user
from models.auth import User, UserRole
import bcrypt # type: ignore
from sqlalchemy.exc import IntegrityError


async def register_admin(db: AsyncSession,*, name: str, email: str, password: str) -> User:
    existing = (await db.execute(select(User).limit(1))).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=400, detail="First admin already registered")
    
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    user_db = User(name=name, email=email, hashed_password=hashed_pw, role=UserRole.admin, is_active=True)
    db.add(user_db)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    await db.refresh(user_db)

    return user_db

async def login(db: AsyncSession,*, email: str, password: str) -> tuple[str, str]:
    user_db = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if user_db is None:
        raise HTTPException(status_code=401, detail="User with this email does not exist")
    if not user_db.is_active:
        raise HTTPException(status_code=403, detail="Access denied")

    is_match = bcrypt.checkpw(password.encode(), user_db.hashed_password)
    if not is_match:
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    access_token = create_access_token(user_id=user_db.id, role=user_db.role)
    return access_token, "bearer"

