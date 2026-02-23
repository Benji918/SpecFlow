from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date, and_, extract
from datetime import datetime, timedelta, date
from typing import List, Optional
from collections import defaultdict
import uuid

from app.database import get_db
from app.models.user import User
from app.models.spec import Spec
from app.models.journey import Journey
from app.models.execution import Execution
from app.schemas.user import UserCreate, UserResponse, AdminCreate, AdminUserUpdate
from app.services.auth import get_current_user, get_password_hash

router = APIRouter(prefix="/api/admin", tags=["admin"])


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin access."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@router.get("/stats")
async def get_dashboard_stats(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get high-level platform statistics for the admin dashboard."""
    # Total users (excluding admins)
    total_users = await db.scalar(select(func.count(User.id)).where(User.is_admin == False))
    free_users = await db.scalar(select(func.count(User.id)).where(User.plan == "free", User.is_admin == False))
    paid_users = total_users - free_users

    # Users by plan breakdown (excluding admins)
    plan_counts = {}
    for plan in ["free", "starter", "team", "pro"]:
        count = await db.scalar(select(func.count(User.id)).where(User.plan == plan, User.is_admin == False))
        plan_counts[plan] = count

    # New users in last 7d & 30d (excluding admins)
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    new_users_7d = await db.scalar(
        select(func.count(User.id)).where(User.created_at >= week_ago, User.is_admin == False)
    )
    new_users_30d = await db.scalar(
        select(func.count(User.id)).where(User.created_at >= month_ago, User.is_admin == False)
    )

    # Specs
    total_specs = await db.scalar(select(func.count(Spec.id)))
    recent_specs_7d = await db.scalar(
        select(func.count(Spec.id)).where(Spec.uploaded_at >= week_ago)
    )

    # Journeys breakdown by generation method
    total_journeys = await db.scalar(select(func.count(Journey.id)))
    ai_journeys = await db.scalar(
        select(func.count(Journey.id)).where(Journey.generation_method == "ai")
    )
    manual_journeys = await db.scalar(
        select(func.count(Journey.id)).where(Journey.generation_method == "manual")
    )

    # Executions
    total_executions = await db.scalar(select(func.count(Execution.id)))
    successful_executions = await db.scalar(
        select(func.count(Execution.id)).where(Execution.status == "completed")
    )
    failed_executions = await db.scalar(
        select(func.count(Execution.id)).where(Execution.status == "failed")
    )
    running_executions = await db.scalar(
        select(func.count(Execution.id)).where(Execution.status == "running")
    )

    success_rate = (
        round((successful_executions / total_executions) * 100, 1)
        if total_executions
        else 0.0
    )

    # Recent executions last 7d
    recent_executions_7d = await db.scalar(
        select(func.count(Execution.id)).where(Execution.started_at >= week_ago)
    )

    return {
        "users": {
            "total": total_users,
            "free": free_users,
            "paid": paid_users,
            "by_plan": plan_counts,
            "new_7d": new_users_7d,
            "new_30d": new_users_30d,
        },
        "specs": {
            "total": total_specs,
            "new_7d": recent_specs_7d,
        },
        "journeys": {
            "total": total_journeys,
            "ai_generated": ai_journeys,
            "manual": manual_journeys,
        },
        "executions": {
            "total": total_executions,
            "successful": successful_executions,
            "failed": failed_executions,
            "running": running_executions,
            "success_rate": success_rate,
            "new_7d": recent_executions_7d,
        },
    }


@router.get("/growth")
async def get_growth_metrics(
    days: int = 30,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get day-by-day growth data over the past N days (default 30)."""
    if days > 90:
        days = 90

    since = datetime.utcnow() - timedelta(days=days)

    # --- Users per day (excluding admins) ---
    user_rows = await db.execute(
        select(cast(User.created_at, Date).label("day"), func.count(User.id).label("count"))
        .where(User.created_at >= since, User.is_admin == False)
        .group_by(cast(User.created_at, Date))
        .order_by(cast(User.created_at, Date))
    )
    user_by_day = {str(r.day): r.count for r in user_rows}

    # --- Specs per day ---
    spec_rows = await db.execute(
        select(cast(Spec.uploaded_at, Date).label("day"), func.count(Spec.id).label("count"))
        .where(Spec.uploaded_at >= since)
        .group_by(cast(Spec.uploaded_at, Date))
        .order_by(cast(Spec.uploaded_at, Date))
    )
    specs_by_day = {str(r.day): r.count for r in spec_rows}

    # --- Executions per day (successful vs failed) ---
    exec_rows = await db.execute(
        select(
            cast(Execution.started_at, Date).label("day"),
            Execution.status,
            func.count(Execution.id).label("count"),
        )
        .where(Execution.started_at >= since)
        .group_by(cast(Execution.started_at, Date), Execution.status)
        .order_by(cast(Execution.started_at, Date))
    )
    exec_success_by_day: dict = defaultdict(int)
    exec_failed_by_day: dict = defaultdict(int)
    for r in exec_rows:
        if r.status == "completed":
            exec_success_by_day[str(r.day)] += r.count
        elif r.status == "failed":
            exec_failed_by_day[str(r.day)] += r.count

    # Build a continuous date list
    dates = [(since + timedelta(days=i)).date() for i in range(days + 1)]
    date_labels = [str(d) for d in dates]

    return {
        "labels": date_labels,
        "users": [user_by_day.get(d, 0) for d in date_labels],
        "specs": [specs_by_day.get(d, 0) for d in date_labels],
        "executions_successful": [exec_success_by_day.get(d, 0) for d in date_labels],
        "executions_failed": [exec_failed_by_day.get(d, 0) for d in date_labels],
    }


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    page: int = 1,
    limit: int = 20,
    plan: Optional[str] = None,
    is_admin: Optional[bool] = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all users with optional plan and admin filter."""
    query = select(User).order_by(User.created_at.desc())
    if plan:
        query = query.where(User.plan == plan)
    if is_admin is not None:
        query = query.where(User.is_admin == is_admin)
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]


@router.post("/create-admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_account(
    user_data: AdminCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new admin account. Only existing admins can do this."""
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    new_admin = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=get_password_hash(user_data.password),
        is_admin=True,
        plan="pro",
    )
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    return UserResponse.model_validate(new_admin)


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get recent executions with journey & user context."""
    exec_result = await db.execute(
        select(Execution)
        .order_by(Execution.started_at.desc())
        .limit(limit)
    )
    executions = exec_result.scalars().all()

    activity = []
    for exe in executions:
        journey_result = await db.execute(
            select(Journey).where(Journey.id == exe.journey_id)
        )
        journey = journey_result.scalar_one_or_none()
        user = None
        if journey:
            user_result = await db.execute(
                select(User).where(User.id == journey.user_id)
            )
            user = user_result.scalar_one_or_none()

        activity.append({
            "execution_id": str(exe.id),
            "status": exe.status,
            "started_at": exe.started_at.isoformat() if exe.started_at else None,
            "completed_at": exe.completed_at.isoformat() if exe.completed_at else None,
            "journey_name": journey.name if journey else "Unknown",
            "journey_id": str(exe.journey_id),
            "user_name": user.name if user else "Unknown",
            "user_email": user.email if user else "Unknown",
        })

    return activity


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: AdminUserUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update a user's details, plan, or admin status."""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update fields if provided
    if user_data.name is not None:
        user.name = user_data.name
    if user_data.email is not None:
        # Check if email is already taken
        if user_data.email != user.email:
            existing = await db.execute(select(User).where(User.email == user_data.email))
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
        user.email = user_data.email
    if user_data.plan is not None:
        user.plan = user_data.plan
    if user_data.is_admin is not None:
        user.is_admin = user_data.is_admin

    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a user account."""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    # Don't let admins delete themselves
    if user_uuid == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own admin account",
        )

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.delete(user)
    await db.commit()
    return None
