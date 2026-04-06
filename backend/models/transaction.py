import uuid

from sqlalchemy import Column
from database import Base
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import ForeignKey
from sqlalchemy.types import Numeric, Date, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy import Enum as SAEnum
from models.category import CashflowTypeEnum
from sqlalchemy import text
from sqlalchemy.types import DateTime


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(PG_UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False, index=True)

    amount = Column(Numeric(12, 2), nullable=False)
    type = Column(SAEnum(CashflowTypeEnum, name="cashflow_type_enum"), nullable=False)

    date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)

    is_deleted = Column(Boolean, nullable=False, server_default=text("false"))

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
