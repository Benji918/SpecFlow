from pydantic import BaseModel, EmailStr, UUID4
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: UUID4
    plan: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    token: str
    user: UserResponse


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
