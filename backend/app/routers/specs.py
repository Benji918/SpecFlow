from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.database import get_db
from app.models.user import User
from app.models.spec import Spec
from app.schemas.spec import SpecCreate, SpecResponse, SpecUpdate
from app.services.auth import get_current_user
from app.services.spec_parser import SpecParser
from app.services.cache import cache_service
from typing import Optional

router = APIRouter(prefix="/api/specs", tags=["specs"])

def get_spec_cache_key(user_id: uuid.UUID, spec_id: Optional[uuid.UUID] = None) -> str:
    if spec_id:
        return f"spec:{user_id}:{spec_id}"
    return f"specs:{user_id}"


@router.post("", response_model=SpecResponse, status_code=status.HTTP_201_CREATED)
async def create_spec(
    spec_data: SpecCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload and validate an OpenAPI specification."""
    try:
        # Parse and validate spec
        parser = SpecParser(spec_data.content)
        endpoints = parser.extract_endpoints()
        schemas = parser.get_schemas()
        version = parser.get_version()
        
        # Convert EndpointInfo objects to dictionaries
        endpoints_dict = [e.model_dump() for e in endpoints]
        
        # Create spec record
        spec = Spec(
            user_id=current_user.id,
            name=spec_data.name,
            version=version,
            content=spec_data.content,
            endpoints=endpoints_dict,
            schemas=schemas,
        )
        
        db.add(spec)
        await db.commit()
        await db.refresh(spec)
        
        # Invalidate list cache
        await cache_service.delete(get_spec_cache_key(current_user.id))
        
        return SpecResponse.model_validate(spec)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OpenAPI specification: {str(e)}",
        )


@router.get("", response_model=List[SpecResponse])
async def list_specs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all specs for the current user."""
    cache_key = get_spec_cache_key(current_user.id)
    cached_data = await cache_service.get(cache_key)
    if cached_data:
        return cached_data

    result = await db.execute(
        select(Spec).where(Spec.user_id == current_user.id).order_by(Spec.uploaded_at.desc())
    )
    specs = result.scalars().all()
    response_data = [SpecResponse.model_validate(spec).model_dump(mode='json') for spec in specs]
    
    await cache_service.set(cache_key, response_data)
    return response_data


@router.get("/{spec_id}", response_model=SpecResponse)
async def get_spec(
    spec_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific spec by ID."""
    # cache_key = get_spec_cache_key(current_user.id, spec_id)
    # cached_data = await cache_service.get(cache_key)
    # if cached_data:
    #     return cached_data

    result = await db.execute(
        select(Spec).where(Spec.id == spec_id, Spec.user_id == current_user.id)
    )
    spec = result.scalar_one_or_none()
    
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spec not found",
        )
    
    response_data = SpecResponse.model_validate(spec).model_dump(mode='json')
    # await cache_service.set(cache_key, response_data)
    return response_data


@router.patch("/{spec_id}", response_model=SpecResponse)
async def update_spec(
    spec_id: uuid.UUID,
    spec_update: SpecUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a spec's metadata."""
    result = await db.execute(
        select(Spec).where(Spec.id == spec_id, Spec.user_id == current_user.id)
    )
    spec = result.scalar_one_or_none()
    
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spec not found",
        )
    
    # Update fields
    if spec_update.name is not None:
        spec.name = spec_update.name
    
    await db.commit()
    await db.refresh(spec)
    
    # Invalidate caches
    await cache_service.delete(get_spec_cache_key(current_user.id, spec_id))
    await cache_service.delete(get_spec_cache_key(current_user.id))
    
    return SpecResponse.model_validate(spec)


@router.delete("/{spec_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_spec(
    spec_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a spec and all associated journeys."""
    result = await db.execute(
        select(Spec).where(Spec.id == spec_id, Spec.user_id == current_user.id)
    )
    spec = result.scalar_one_or_none()
    
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spec not found",
        )
    
    await db.delete(spec)
    await db.commit()
    
    # Invalidate caches
    await cache_service.delete(get_spec_cache_key(current_user.id, spec_id))
    await cache_service.delete(get_spec_cache_key(current_user.id))
    # Also invalidate journeys list as they might be deleted cascade
    await cache_service.delete(f"journeys:{current_user.id}")
