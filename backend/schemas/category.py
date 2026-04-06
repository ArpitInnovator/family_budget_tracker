from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from models.category import CashflowTypeEnum


class CategoryCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: CashflowTypeEnum

class CategoryResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    type: CashflowTypeEnum
    created_at: datetime