from pydantic import BaseModel, EmailStr, UUID4, field_validator
from datetime import datetime
from typing import Optional
import re


def validate_email_domain_logic(v: str) -> str:
    # Basic sanitization
    v = v.strip().lower()
    if not v:
        raise ValueError("Email cannot be empty")
    
    # SQL Injection prevention
    if any(char in v for char in ["'", '"', ";", "\\"]):
        raise ValueError("Invalid characters in email")

    # Domain validation
    if "@" not in v:
        raise ValueError("Invalid email format")
        
    domain = v.split("@")[1]
    if "." not in domain or len(domain.split(".")) < 2:
        raise ValueError("Email must have a valid domain (e.g., example.com)")
    
    return v


def sanitize_name_logic(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    # Strip HTML tags
    v = re.sub(r'<[^>]*>?', '', v).strip()
    # SQL Injection prevention
    if any(char in v for char in ["'", '"', ";", "\\"]):
        raise ValueError("Invalid characters in name")
    return v


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

    model_config = {
        "extra": "forbid"
    }

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return validate_email_domain_logic(v)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        return sanitize_name_logic(v)


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: UUID4
    plan: str
    is_admin: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class AdminCreate(UserCreate):
    """Schema for creating an admin account."""
    is_admin: bool = True
    

class UserWithTokenResponse(UserResponse):
    """User response with token for WebSocket authentication."""
    token: Optional[str] = None

class TokenResponse(BaseModel):
    token: str
    user: UserResponse


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[EmailStr]) -> Optional[EmailStr]:
        if v is None:
            return v
        return validate_email_domain_logic(v)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        return sanitize_name_logic(v)


class AdminUserUpdate(UserUpdate):
    """Schema for admins to update any user's properties."""
    plan: Optional[str] = None
    is_admin: Optional[bool] = None
