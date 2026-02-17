from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
import re
import asyncio
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
from app.services.auth import get_current_user, verify_token
from app.services.spec_parser import SpecParser, EndpointInfo
from app.services.journey_generator import JourneyGenerator
from app.services.cache import cache_service
from typing import Optional

router = APIRouter(prefix="/api", tags=["journeys"])

def get_journey_cache_key(user_id: uuid.UUID, journey_id: Optional[uuid.UUID] = None) -> str:
    if journey_id:
        return f"journey:{user_id}:{journey_id}"
    return f"journeys:{user_id}"


# @router.post(
#     "/specs/{spec_id}/generate-journeys",
#     response_model=List[JourneyResponse],
#     status_code=status.HTTP_201_CREATED,
# )
# async def generate_journeys(
#     spec_id: uuid.UUID,
#     request: GenerateJourneysRequest,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     """Generate journeys from a spec using AI."""
#     # Verify spec ownership
#     result = await db.execute(
#         select(Spec).where(Spec.id == spec_id, Spec.user_id == current_user.id)
#     )
#     spec = result.scalar_one_or_none()
    
#     if not spec:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Spec not found",
#         )
    
#     # Parse spec to get endpoints
#     parser = SpecParser(spec.content)
#     endpoints = parser.extract_endpoints()
    
#     if request.strategy == "ai":
#         # Generate journeys using AI
#         generator = JourneyGenerator()
#         try:
#             journey_data_list = await generator.generate_journeys(endpoints)
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"AI journey generation failed: {str(e)}",
#             )
#     else:
#         # Manual strategy - create a basic journey
#         journey_data_list = [
#             {
#                 "name": "Manual Journey",
#                 "description": "Manually created journey",
#                 "nodes": [],
#                 "edges": [],
#             }
#         ]
    
#     # Save journeys to database
#     created_journeys = []
#     for journey_data in journey_data_list:
#         journey = Journey(
#             user_id=current_user.id,
#             spec_id=spec_id,
#             name=journey_data["name"],
#             nodes=journey_data["nodes"],
#             edges=journey_data["edges"],
#             generation_method=request.strategy,
#         )
#         db.add(journey)
#         created_journeys.append(journey)
    
#     await db.commit()
    
#     # Refresh all journeys
#     # Invalidate list cache
#     cache_service.delete(get_journey_cache_key(current_user.id))
    
#     return [JourneyResponse.model_validate(j) for j in created_journeys]

@router.websocket("/ws/specs/{spec_id}/generate-journeys")
async def websocket_generate_journeys(websocket: WebSocket, spec_id: uuid.UUID):
    """WebSocket endpoint for journey generation."""
    await websocket.accept()
    
    try:
        # First try to get token from cookie
        token = ""
        cookies = websocket.cookies
        if cookies and "access_token" in cookies:
            token = cookies.get("access_token")
            print("Token from cookie:", token)
        else:
            # Try from headers
            headers = dict(websocket.headers)
            cookie_header = headers.get("cookie", "")
            for cookie in cookie_header.split(";"):
                if "access_token" in cookie:
                    token = cookie.split("=")[1].strip()
                    print("Token from header:", token)
                    break
        
        # Get strategy from client message
        try:
            auth_data = await websocket.receive_json()
            strategy = auth_data.get("strategy", "ai")
            # If no token from cookie, try getting from message
            if not token and auth_data.get("token"):
                token = auth_data.get("token")
                print("Token from message:", token)
        except:
            strategy = "ai"
        
        async for db in get_db():
            try:
                # Authenticate
                payload = verify_token(token)
                user_id = payload.get("sub")
                result = await db.execute(select(User).where(User.id == user_id))
                current_user = result.scalar_one_or_none()
                
                if not current_user:
                    await websocket.send_json({"type": "error", "message": "Auth failed"})
                    return
                
                # Get spec
                result = await db.execute(
                    select(Spec).where(
                        Spec.id == spec_id,
                        Spec.user_id == current_user.id
                    )
                )
                spec = result.scalar_one_or_none()
                
                if not spec:
                    await websocket.send_json({"type": "error", "message": "Spec not found"})
                    return
                
                parser = SpecParser(spec.content)
                endpoints = parser.extract_endpoints()
                
                if strategy == "ai":
                    # Generate journeys using AI
                    generator = JourneyGenerator()
                    try:
                        journey_data_list = await generator.generate_journeys(endpoints, websocket=websocket)
                    except Exception as e:
                        await websocket.send_json({"type": "error", 
                                                   "message": f"AI journey generation failed: {str(e)}"
                                                   })
                        return
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
                
                # Save to database
                created_journeys = []
                for journey_data in journey_data_list:
                    journey = Journey(
                        user_id=current_user.id,
                        spec_id=spec_id,
                        name=journey_data["name"],
                        nodes=journey_data["nodes"],
                        edges=journey_data["edges"],
                        generation_method=strategy,
                    )
                    db.add(journey)
                    created_journeys.append(journey)
                
                await db.commit()
                
                for journey in created_journeys:
                    await db.refresh(journey)
                
                await cache_service.delete(get_journey_cache_key(current_user.id))
                
                # Send result
                journey_responses = [{
                    "id": str(j.id),
                    "spec_id": str(j.spec_id),
                    "name": j.name,
                    "nodes": j.nodes,
                    "edges": j.edges,
                    "generation_method": j.generation_method,
                    "created_at": j.created_at.isoformat() if j.created_at else None,
                } for j in created_journeys]
                
                await websocket.send_json({
                    "type": "complete",
                    "data": journey_responses,
                    "message": f"Generated {len(journey_responses)} journey(s)!"
                })
                
            except Exception as e:
                await websocket.send_json({"type": "error", "message": str(e)})
            finally:
                await websocket.close()
                db.rollback()
                break
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {spec_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        

@router.get("/journeys", response_model=List[JourneyResponse])
async def list_journeys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all journeys for the current user."""
    cache_key = get_journey_cache_key(current_user.id)
    cached_data = await cache_service.get(cache_key)
    if cached_data:
        return cached_data

    result = await db.execute(
        select(Journey)
        .where(Journey.user_id == current_user.id)
        .order_by(Journey.created_at.desc())
    )
    journeys = result.scalars().all()
    response_data = [JourneyResponse.model_validate(j).model_dump(mode='json') for j in journeys]
    
    await cache_service.set(cache_key, response_data)
    return response_data

@router.get("/journeys/{journey_id}", response_model=JourneyResponse)
async def get_journey(
    journey_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific journey by ID."""
    cache_key = get_journey_cache_key(current_user.id, journey_id)
    cached_data = await cache_service.get(cache_key)
    if cached_data:
        return cached_data

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
    
    response_data = JourneyResponse.model_validate(journey).model_dump(mode='json')
    asyncio.create_task(cache_service.set(cache_key, response_data))
    return response_data



def is_auth_endpoint(endpoint_data: dict) -> bool:
    """Check if an endpoint is likely an authentication endpoint."""
    path = endpoint_data.get("path", "").lower()
    summary = (endpoint_data.get("summary") or "").lower()
    op_id = (endpoint_data.get("operation_id") or "").lower()
    
    keywords = ["login", "token", "auth", "signin", "authenticate", "session"]
    return any(k in path or k in summary or k in op_id for k in keywords)


def validate_unique_nodes(nodes: List[dict]):
    """Ensure no duplicate endpoints (method + path) exist in the node list."""
    seen = set()
    for node in nodes:
        data = node.get("data", {})
        # Create a unique key for the endpoint
        key = (data.get("method", "").upper(), data.get("path", ""))
        
        # Skip validation for non-endpoint nodes if any (e.g. specialized logic nodes in future)
        if not key[0] or not key[1]:
            continue
            
        if key in seen:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Duplicate endpoint detected: {key[0]} {key[1]}. A journey cannot contain the same endpoint multiple times."
            )
        seen.add(key)


def validate_journey_name(name: str):
    """Validate journey name for potential security threats (XSS/SQLi)."""
    if not name or not name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Journey name cannot be empty."
        )
    
    # Basic XSS patterns
    xss_pattern = re.compile(r"(?:<script|javascript:|onload=|onerror=|onclick=|<iframe|<object|<embed)", re.IGNORECASE)
    if xss_pattern.search(name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security Verification Failed: Invalid characters detected in journey name."
        )

    # Basic SQL Injection patterns
    sql_pattern = re.compile(r"(?:'|--|;|drop\s+table|delete\s+from|insert\s+into|update.*set|select.*from|union\s+select)", re.IGNORECASE)
    if sql_pattern.search(name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security Verification Failed: Invalid pattern detected in journey name."
        )


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
    
    # Validate name
    validate_journey_name(journey_data.name)

    # Validate nodes
    if journey_data.nodes:
        # Check 1: First node must be auth
        first_node = journey_data.nodes[0]
        node_data = first_node.get("data", {})
        if not is_auth_endpoint(node_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security Validation: The first node of a journey must be an authentication endpoint (e.g., Login or Token extraction)."
            )
        
        # Check 2: No duplicates
        validate_unique_nodes(journey_data.nodes)
    
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
    
    # Invalidate list cache
    await cache_service.delete(get_journey_cache_key(current_user.id))
    
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
        validate_journey_name(journey_update.name)
        journey.name = journey_update.name
    if journey_update.nodes is not None:
        validate_unique_nodes(journey_update.nodes)
        journey.nodes = journey_update.nodes
    if journey_update.edges is not None:
        journey.edges = journey_update.edges
    
    await db.commit()
    await db.refresh(journey)
    
    # Invalidate caches
    await asyncio.gather(
        cache_service.delete(get_journey_cache_key(current_user.id, journey_id)),
        cache_service.delete(get_journey_cache_key(current_user.id))
    )
    
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
    
    # Invalidate caches
    await asyncio.gather(
        cache_service.delete(get_journey_cache_key(current_user.id, journey_id)),
        cache_service.delete(get_journey_cache_key(current_user.id))
    )
