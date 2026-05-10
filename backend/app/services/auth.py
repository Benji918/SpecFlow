from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status, Request, WebSocket
from starlette.requests import HTTPConnection
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Union
import uuid
from app.config import settings
from app.database import get_db
from app.models.user import User

# Password hashing context
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# HTTP Bearer for token
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None,
    auth_method: str = "email"
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire, "auth_method": auth_method})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    request: HTTPConnection,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT token (header or cookie)."""
    token = None
    
    # Try to get from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    # Try to get from cookie if not in header
    if not token:
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = verify_token(token)
    
async def get_user_from_token_payload(payload: dict, db: AsyncSession) -> Optional[User]:
    """Get user from decoded token payload, supporting both UUID and email."""
    user_id: str = payload.get("sub")
    if user_id is None:
        return None
    
    # Support both UUID (normal users) and email (newly authenticated OAuth users)
    is_uuid = False
    try:
        if isinstance(user_id, str):
            uuid.UUID(user_id)
            is_uuid = True
    except (ValueError, TypeError, AttributeError):
        is_uuid = False

    if is_uuid:
        result = await db.execute(select(User).where(User.id == user_id))
    else:
        # Try finding by email (for newly created OAuth users whose ID we don't put in token yet)
        result = await db.execute(select(User).where(User.email == user_id))
    
    return result.scalar_one_or_none()


async def get_current_user(
    request: HTTPConnection,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT token (header or cookie)."""
    token = None
    
    # Try to get from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    # Try to get from cookie if not in header
    if not token:
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = verify_token(token)
    user = await get_user_from_token_payload(payload, db)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    
    return user
