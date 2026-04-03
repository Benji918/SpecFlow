from datetime import timedelta
from typing import Annotated
from fastapi import Depends, Request, APIRouter, BackgroundTasks, Response
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
import os
from app.services.auth import create_access_token
from app.config import settings, Settings
from functools import lru_cache
import logging
from app.database import get_db
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/google-auth", tags=["google-auth"])

@lru_cache
def get_settings():
    return settings

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    userinfo_endpoint="https://www.googleapis.com/oauth2/v2/userinfo",
    api_base_url= "https://www.googleapis.com/oauth2/v3/",
    client_kwargs={"scope": "openid email profile"},
    server_metadata_url= 'https://accounts.google.com/.well-known/openid-configuration'
)

# Redirect user to Google for authentication
@router.get("/google")
async def auth_google(request: Request):
    """
    Initiates Google OAuth flow. 
    If user already has a valid token cookie, we could redirect to dashboard,
    but standard practice is to proceed with OAuth as an explicit action.
    """
    # Use X-Forwarded-Proto if behind a proxy, otherwise fallback to request scheme
    scheme = request.headers.get("X-Forwarded-Proto", request.url.scheme)
    # Ensure scheme is https if not local
    if "backend.specflow.pro" in request.url.netloc:
        scheme = "https"
        
    base_url = f"{scheme}://{request.url.netloc}"
    redirect_url = f"{base_url}/api/google-auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri=redirect_url)


# Handle the OAuth callback from Google
@router.get("/callback")
async def google_callback(
    request: Request, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    try:
        user_created = False
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo") or {}

        # Extract user details
        email = user_info.get("email") 
        name = user_info.get("name")

        if not email:
            return {"error": "Email not provided by Google"}

        # Quick check for existing user
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        # Determine the stable identifier
        sub = str(user.id) if user else email
        if not user:
            user_created = True

        # Sync user to DB in background
        background_tasks.add_task(create_user_from_google, email, name)

        # Create access token valid for 1 week
        token_expires = timedelta(days=7)
        access_token = create_access_token(
            data={"sub": sub}, 
            expires_delta=token_expires,
            auth_method="google"
        )

        frontend_base = settings.frontend_url

        redirect_url = f"{frontend_base}/dashboard?auth_success=true&is_new={str(user_created).lower()}"
        response = RedirectResponse(url=redirect_url)

        # Set HttpOnly cookie for 1 week
        cookie_max_age = int(token_expires.total_seconds())
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=cookie_max_age,
            expires=cookie_max_age,
            secure=True if not settings.DEBUG else False,
            samesite="lax" if settings.DEBUG else "none",
        )

        return response
    except Exception as e:
        import traceback
        logger.error(f"Google login failed: {traceback.format_exc()}")
 
        frontend_base = settings.frontend_url
                 
        return RedirectResponse(url=f"{frontend_base}/login?error={str(e)}")

async def create_user_from_google(email: str, name: str):
    """Background task to sync Google user to local database."""
    from app.database import AsyncSessionLocal
    from app.models.user import User
    from app.services.auth import get_password_hash
    from sqlalchemy import select
    import uuid
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if user already exists
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            
            if not user:
                # Create new user for first-time Google sign-in
                user = User(
                    email=email,
                    name=name,
                    sign_up_method="google",
                    # Google users don't have a password, so hash a random UUID
                    password_hash=get_password_hash(str(uuid.uuid4()))
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
        except Exception as e:
            logger.error(f"Error creating user from Google in background: {e}")
            await db.rollback()
