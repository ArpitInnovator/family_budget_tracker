from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from models.auth import UserRole
from pydantic import ConfigDict
from uuid import UUID

class AdminCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8)

class LoginRequestSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"



