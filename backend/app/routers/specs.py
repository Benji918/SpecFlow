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

router = APIRouter(prefix="/api/specs", tags=["specs"])


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
    result = await db.execute(
        select(Spec).where(Spec.user_id == current_user.id).order_by(Spec.uploaded_at.desc())
    )
    specs = result.scalars().all()
    return [SpecResponse.model_validate(spec) for spec in specs]


@router.get("/{spec_id}", response_model=SpecResponse)
async def get_spec(
    spec_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific spec by ID."""
    result = await db.execute(
        select(Spec).where(Spec.id == spec_id, Spec.user_id == current_user.id)
    )
    spec = result.scalar_one_or_none()
    
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spec not found",
        )
    
    return SpecResponse.model_validate(spec)


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
