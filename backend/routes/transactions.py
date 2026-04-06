from fastapi import APIRouter,status, Query
from schemas.transaction import TransactionCreateSchema,TransactionResponseSchema,TransactionUpdateSchema
from models.auth import UserRole
from services import transaction_service
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from core.access_control import require_roles
from fastapi import Depends
from typing import List, Optional
from datetime import date
from uuid import UUID
from models.category import CashflowTypeEnum
 


router = APIRouter(prefix="/transactions", tags=["transactions"])
ROLES_ALLOWED = (UserRole.admin, UserRole.analyst)

@router.post("", status_code = status.HTTP_201_CREATED, response_model=TransactionResponseSchema)
async def create_transaction(
    payload: TransactionCreateSchema,
    db: AsyncSession = Depends(get_db),
    _admin_user=Depends(require_roles(UserRole.admin)),
):
    return await transaction_service.create_transaction(
        db,
        user_id=payload.user_id,
        category_id=payload.category_id,
        amount=payload.amount,
        type=payload.type,
        txn_date=payload.date,
        notes=payload.notes,
    )

@router.get("", response_model=List[TransactionResponseSchema])
async def list_transactions(
    type: Optional[CashflowTypeEnum] = Query(default=None),
    category_id: Optional[UUID] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    search: Optional[str] = Query(default=None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(require_roles(*ROLES_ALLOWED)),
):
    return await transaction_service.list_transactions(
        db,
        type=type,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
        search=search,
        skip=skip,
        limit=limit,
    )

@router.get("/{id}", response_model=TransactionResponseSchema)
async def get_transaction(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(require_roles(*ROLES_ALLOWED)),
):
    return await transaction_service.get_transaction(db, transaction_id=id)


@router.patch("/{id}", response_model=TransactionResponseSchema)
async def update_transaction(
    id: UUID,
    payload: TransactionUpdateSchema,
    db: AsyncSession = Depends(get_db),
    admin_user=Depends(require_roles(UserRole.admin)),
):
    return await transaction_service.update_transaction(
        db,
        _admin_user_id=admin_user.id,
        transaction_id=id,
        user_id=payload.user_id,
        category_id=payload.category_id,
        amount=payload.amount,
        type=payload.type,
        txn_date=payload.date,
        notes=payload.notes,
    )

@router.delete("/{id}", response_model=TransactionResponseSchema)
async def soft_delete_transaction(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    admin_user=Depends(require_roles(UserRole.admin)),
):
    return await transaction_service.soft_delete_transaction(
        db,
        _admin_user_id=admin_user.id,
        transaction_id=id,
    )

