from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.journey import Journey
from app.models.execution import Execution
from app.schemas.execution import ExecutionResponse
from app.services.auth import get_current_user
from app.services.journey_executor import JourneyExecutor

router = APIRouter(prefix="/api", tags=["execution"])


@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific execution by ID."""
    result = await db.execute(select(Execution).where(Execution.id == execution_id))
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found",
        )
    
    # Verify journey ownership
    journey_result = await db.execute(
        select(Journey).where(
            Journey.id == execution.journey_id, Journey.user_id == current_user.id
        )
    )
    journey = journey_result.scalar_one_or_none()
    
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    return ExecutionResponse.model_validate(execution)


@router.get("/journeys/{journey_id}/executions", response_model=List[ExecutionResponse])
async def list_journey_executions(
    journey_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get execution history for a journey."""
    # Verify journey ownership
    journey_result = await db.execute(
        select(Journey).where(
            Journey.id == journey_id, Journey.user_id == current_user.id
        )
    )
    journey = journey_result.scalar_one_or_none()
    
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journey not found",
        )
    
    # Get executions
    result = await db.execute(
        select(Execution)
        .where(Execution.journey_id == journey_id)
        .order_by(Execution.started_at.desc())
    )
    executions = result.scalars().all()
    
    return [ExecutionResponse.model_validate(e) for e in executions]


@router.websocket("/ws/journey/{journey_id}/execute")
async def execute_journey_ws(websocket: WebSocket, journey_id: str):
    """Execute a journey via WebSocket with real-time updates."""
    await websocket.accept()
    
    try:
        # Get database session
        async for db in get_db():
            # Get execution parameters from client
            data = await websocket.receive_json()
            base_url = data.get("baseUrl")
            session_data = data.get("sessionData", {})
            error_injections = data.get("error Injections", {})
            
            if not base_url:
                await websocket.send_json({
                    "type": "error",
                    "message": "baseUrl is required"
                })
                await websocket.close()
                return
            
            # Fetch journey
            journey_uuid = uuid.UUID(journey_id)
            result = await db.execute(
                select(Journey).where(Journey.id == journey_uuid)
            )
            journey = result.scalar_one_or_none()
            
            if not journey:
                await websocket.send_json({
                    "type": "error",
                    "message": "Journey not found"
                })
                await websocket.close()
                return
            
            # Create execution record
            execution = Execution(
                journey_id=journey_uuid,
                status="running",
            )
            db.add(execution)
            await db.commit()
            await db.refresh(execution)
            
            # Initialize executor
            executor = JourneyExecutor(base_url)
            
            # Execute journey
            nodes = journey.nodes
            edges = journey.edges
            results = []
            
            for node in nodes:
                # Send step start event
                await websocket.send_json({
                    "type": "step_start",
                    "stepId": node["id"]
                })
                
                # Execute step
                step_id = node["id"]
                if step_id in error_injections:
                    result = executor._inject_error(node, error_injections[step_id])
                else:
                    result = await executor._execute_step(node, session_data)
                
                # Send step result
                await websocket.send_json({
                    "type": "step_result",
                    "result": result
                })
                
                # Update session for next steps
                executor._update_session_data(session_data, result, edges)
                
                # Store result
                results.append(result)
                execution.results = results
                await db.commit()
                
                # Stop on error if needed
                status_code = result.get("statusCode", 0)
                continue_on_error = node.get("data", {}).get("continueOnError", False)
                
                if status_code >= 400 and not continue_on_error:
                    execution.status = "failed"
                    break
            
            # Mark execution complete
            if execution.status == "running":
                execution.status = "completed"
            execution.completed_at = datetime.utcnow()
            await db.commit()
            
            # Send completion event
            await websocket.send_json({
                "type": "execution_complete",
                "executionId": str(execution.id),
                "status": execution.status
            })
            
            # Close executor
            await executor.close()
            
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for journey {journey_id}")
    except Exception as e:
        print(f"Error executing journey {journey_id}: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass
