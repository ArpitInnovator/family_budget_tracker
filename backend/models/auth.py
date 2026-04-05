from enum import Enum
from sqlalchemy import Column, TEXT, String, LargeBinary
from database import Base
from datetime import datetime
from sqlalchemy.types import Boolean, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import text
import uuid

class UserRole(str, Enum):
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"

class User(Base):
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True,index=True)
    hashed_password = Column(LargeBinary, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    role = Column(SAEnum(UserRole, name="user_role_enum"), nullable=False)

