from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.database import get_db
from app.models.user import User
from app.models.spec import Spec
from app.models.journey import Journey
from app.schemas.journey import (
    JourneyCreate,
    JourneyResponse,
    JourneyUpdate,
    GenerateJourneysRequest,
)
from app.services.auth import get_current_user
from app.services.spec_parser import SpecParser, EndpointInfo
from app.services.journey_generator import JourneyGenerator

router = APIRouter(prefix="/api", tags=["journeys"])


@router.post(
    "/specs/{spec_id}/generate-journeys",
    response_model=List[JourneyResponse],
    status_code=status.HTTP_201_CREATED,
)
async def generate_journeys(
    spec_id: uuid.UUID,
    request: GenerateJourneysRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate journeys from a spec using AI."""
    # Verify spec ownership
    result = await db.execute(
        select(Spec).where(Spec.id == spec_id, Spec.user_id == current_user.id)
    )
    spec = result.scalar_one_or_none()
    
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spec not found",
        )
    
    # Parse spec to get endpoints
    parser = SpecParser(spec.content)
    endpoints = parser.extract_endpoints()
    
    if request.strategy == "ai":
        # Generate journeys using AI
        generator = JourneyGenerator()
        try:
            journey_data_list = await generator.generate_journeys(endpoints)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI journey generation failed: {str(e)}",
            )
    else:
        # Manual strategy - create a basic journey
        journey_data_list = [
            {
                "name": "Manual Journey",
                "description": "Manually created journey",
                "nodes": [],
                "edges": [],
            }
        ]
    
    # Save journeys to database
    created_journeys = []
    for journey_data in journey_data_list:
        journey = Journey(
            user_id=current_user.id,
            spec_id=spec_id,
            name=journey_data["name"],
            nodes=journey_data["nodes"],
            edges=journey_data["edges"],
            generation_method=request.strategy,
        )
        db.add(journey)
        created_journeys.append(journey)
    
    await db.commit()
    
    # Refresh all journeys
    for journey in created_journeys:
        await db.refresh(journey)
    
    return [JourneyResponse.model_validate(j) for j in created_journeys]


@router.get("/journeys", response_model=List[JourneyResponse])
async def list_journeys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all journeys for the current user."""
    result = await db.execute(
        select(Journey)
        .where(Journey.user_id == current_user.id)
        .order_by(Journey.created_at.desc())
    )
    journeys = result.scalars().all()
    return [JourneyResponse.model_validate(j) for j in journeys]


@router.get("/journeys/{journey_id}", response_model=JourneyResponse)
async def get_journey(
    journey_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific journey by ID."""
    result = await db.execute(
        select(Journey).where(
            Journey.id == journey_id, Journey.user_id == current_user.id
        )
    )
    journey = result.scalar_one_or_none()
    
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journey not found",
        )
    
    return JourneyResponse.model_validate(journey)


@router.post("/journeys", response_model=JourneyResponse, status_code=status.HTTP_201_CREATED)
async def create_journey(
    journey_data: JourneyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new journey manually."""
    # Verify spec ownership
    result = await db.execute(
        select(Spec).where(
            Spec.id == journey_data.spec_id, Spec.user_id == current_user.id
        )
    )
    spec = result.scalar_one_or_none()
    
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spec not found",
        )
    
    # Create journey
    journey = Journey(
        user_id=current_user.id,
        spec_id=journey_data.spec_id,
        name=journey_data.name,
        nodes=journey_data.nodes,
        edges=journey_data.edges,
        generation_method=journey_data.generation_method or "manual",
    )
    
    db.add(journey)
    await db.commit()
    await db.refresh(journey)
    
    return JourneyResponse.model_validate(journey)


@router.put("/journeys/{journey_id}", response_model=JourneyResponse)
async def update_journey(
    journey_id: uuid.UUID,
    journey_update: JourneyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a journey's nodes, edges, or name."""
    result = await db.execute(
        select(Journey).where(
            Journey.id == journey_id, Journey.user_id == current_user.id
        )
    )
    journey = result.scalar_one_or_none()
    
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journey not found",
        )
    
    # Update fields
    if journey_update.name is not None:
        journey.name = journey_update.name
    if journey_update.nodes is not None:
        journey.nodes = journey_update.nodes
    if journey_update.edges is not None:
        journey.edges = journey_update.edges
    
    await db.commit()
    await db.refresh(journey)
    
    return JourneyResponse.model_validate(journey)


@router.delete("/journeys/{journey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journey(
    journey_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a journey."""
    result = await db.execute(
        select(Journey).where(
            Journey.id == journey_id, Journey.user_id == current_user.id
        )
    )
    journey = result.scalar_one_or_none()
    
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journey not found",
        )
    
    await db.delete(journey)
    await db.commit()
