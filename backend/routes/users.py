from fastapi import APIRouter, Depends, status, Query
from typing import List
from schemas.user import UserCreateSchema, UserResponseSchema, UserUpdateSchema
from models.auth import UserRole
from core.access_control import require_roles
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services import user_service
from uuid import UUID

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/create" , status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema)
async def create_user(
     payload: UserCreateSchema,
     db: AsyncSession = Depends(get_db),
    _admin_user=Depends(require_roles(UserRole.admin)),
    ):
 return await user_service.create_user(
        db,
        name=payload.name,
        email=str(payload.email),
        password=payload.password,
        role=payload.role,
    )

@router.get("", response_model=List[UserResponseSchema])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _admin_user=Depends(require_roles(UserRole.admin)),
):
    return await user_service.list_users(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=UserResponseSchema)
async def get_user(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin_user=Depends(require_roles(UserRole.admin)),
):
    return await user_service.get_user(db, user_id=id)

@router.patch("/{id}", response_model=UserResponseSchema)
async def update_user(
    id: UUID,
    payload: UserUpdateSchema,
    db: AsyncSession = Depends(get_db),
    admin_user=Depends(require_roles(UserRole.admin)),
):
    return await user_service.update_user(
        db,
        admin_user=admin_user,
        user_id=id,
        name=payload.name,
        role=payload.role,
        is_active=payload.is_active,
    )

@router.delete("/{id}", response_model=UserResponseSchema)
async def delete_user(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    admin_user=Depends(require_roles(UserRole.admin)),
):
    return await user_service.delete_user(db, admin_user=admin_user, user_id=id)