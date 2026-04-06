from pydantic import BaseModel, Field, ConfigDict
from datetime import date  , datetime
from uuid import UUID
from decimal import Decimal
from typing import Optional
from models.category import CashflowTypeEnum
from pydantic import field_validator


class TransactionCreateSchema(BaseModel):
    user_id: UUID
    category_id: UUID
    amount: Decimal = Field(gt=0)
    type: CashflowTypeEnum
    date: date
    notes: Optional[str] = None

    @field_validator("date")
    @classmethod
    def validate_not_in_future(cls, v: date) -> date:
        today = date.today()
        if v > today:
            raise ValueError("date must not be in the future")
        return v

class TransactionUpdateSchema(BaseModel):
    user_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    type: Optional[CashflowTypeEnum] = None
    date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("date")
    @classmethod
    def validate_not_in_future(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return v
        today = date.today()
        if v > today:
            raise ValueError("date must not be in the future")
        return v



class TransactionResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    category_id: UUID
    amount: Decimal
    type: CashflowTypeEnum
    date: date
    notes: Optional[str]
    is_deleted: bool
    created_at: datetime
    updated_at: datetime