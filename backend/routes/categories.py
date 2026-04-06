from fastapi import APIRouter
from schemas.category import CategoryCreateSchema, CategoryResponseSchema
from services import category_service
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from core.access_control import require_roles
from models.auth import UserRole
from fastapi import Depends, status
from typing import List


router = APIRouter(prefix="/categories", tags=["categories"])

ROLES_ALLOWED = (UserRole.admin, UserRole.analyst)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=CategoryResponseSchema)
async def create_category(
     payload: CategoryCreateSchema,
     db: AsyncSession = Depends(get_db),
    _admin_user=Depends(require_roles(UserRole.admin)),
):
     return await category_service.create_category(db, name=payload.name, type=payload.type)


@router.get("", response_model=List[CategoryResponseSchema])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(require_roles(*ROLES_ALLOWED)),
):
    return await category_service.list_categories(db)