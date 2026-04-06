from enum import Enum
from sqlalchemy import Column, DateTime, Enum as SAEnum, String, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from database import Base
from datetime import datetime
import uuid
from sqlalchemy.sql import func

class CashflowTypeEnum(str, Enum):
    income = "income"
    expense = "expense"

class Category(Base):
    __tablename__ = "categories"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(SAEnum(CashflowTypeEnum, name="cashflow_type_enum"), nullable=False)
    created_at = Column(DateTime, nullable=False,  server_default=func.now())