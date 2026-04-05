from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.auth import UserRole
from database import get_db
from schemas.auth import AdminCreate, LoginRequestSchema, TokenResponseSchema
from services import auth_service
from schemas.user import UserResponseSchema
from core.access_control import require_roles

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/admin/create" , status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema)
async def create_admin(admin: AdminCreate, db: AsyncSession =  Depends(get_db)):
     return await auth_service.register_admin(db, name=admin.name, email=admin.email, password=admin.password)


@router.post("/login", response_model=TokenResponseSchema)
async def login(
    payload: LoginRequestSchema,
    db: AsyncSession = Depends(get_db),
):
    access_token, token_type = await auth_service.login(db, email=payload.email, password=payload.password)
    return {"access_token": access_token, "token_type": token_type}

@router.get("/me", response_model=UserResponseSchema)
async def me(
    current_user=Depends(require_roles(UserRole.admin, UserRole.analyst, UserRole.viewer)),
):
    return current_user
