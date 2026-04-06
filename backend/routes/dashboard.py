from fastapi import APIRouter
from models.auth import UserRole
from schemas.dashboard import DashboardSummaryResponseSchema, DashboardCategoryTotalsResponseSchema, DashboardRecentActivityResponseSchema
from services import dashboard_service
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from core.access_control import require_roles
from fastapi import Depends, Query
from typing import List
from datetime import date
from uuid import UUID
from models.category import CashflowTypeEnum

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

ALL_ROLES = (UserRole.admin, UserRole.analyst, UserRole.viewer)

@router.get("/monthly-summary", response_model=DashboardSummaryResponseSchema)
async def dashboard_summary(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=1900, le=3000),
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(require_roles(*ALL_ROLES)),
):
    return await dashboard_service.summary(db, month=month, year=year)

@router.get("/category-totals", response_model=DashboardCategoryTotalsResponseSchema)
async def category_totals(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=1900, le=3000),
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(require_roles(*ALL_ROLES)),
):
    items = await dashboard_service.category_totals(db, month=month, year=year)
    return {"items": items}


@router.get("/recent-activity", response_model=DashboardRecentActivityResponseSchema)
async def recent_activity(
    db: AsyncSession = Depends(get_db),
    _current_user=Depends(require_roles(*ALL_ROLES)),
):
    items = await dashboard_service.recent_activity(db)
    return {"items": items}