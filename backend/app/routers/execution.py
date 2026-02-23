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
            # Authenticate user via cookies/headers
            try:
                current_user = await get_current_user(websocket, db)
            except HTTPException as e:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Authentication failed: {e.detail}"
                })
                return
            
            # Get execution parameters from client
            data = await websocket.receive_json()
            base_url = data.get("baseUrl")
            session_data = data.get("sessionData", {})
            error_injections = data.get("errorInjections", {})
            
            if not base_url:
                await websocket.send_json({
                    "type": "error",
                    "message": "baseUrl is required"
                })
                return
            
            # Fetch journey
            journey_uuid = uuid.UUID(journey_id)
            result = await db.execute(
                select(Journey).where(
                    Journey.id == journey_uuid,
                    Journey.user_id == current_user.id
                )
            )
            journey = result.scalar_one_or_none()
            
            if not journey:
                await websocket.send_json({
                    "type": "error",
                    "message": "Journey not found or access denied"
                })
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
            try:
                # Execute journey - use nodes/edges from client if provided (for unsaved mock data)
                nodes = data.get("nodes", journey.nodes)
                edges = data.get("edges", journey.edges)
                results = []
                failed_steps = []
                
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
                    
                    # Track failed steps
                    status_code = result.get("statusCode", 0)
                    if status_code >= 400 or result.get("error"):
                        failed_steps.append({
                            "stepId": step_id,
                            "stepName": node.get("data", {}).get("summary") or node.get("data", {}).get("path", "Unknown"),
                            "statusCode": status_code,
                            "error": result.get("error")
                        })
                    
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
                    continue_on_error = node.get("data", {}).get("continueOnError", False)
                    
                    if status_code >= 400 and not continue_on_error:
                        execution.status = "failed"
                        break
                
                # Mark execution status based on failures
                if failed_steps:
                    execution.status = "failed"
                elif execution.status == "running":
                    execution.status = "completed"
                execution.completed_at = datetime.utcnow()
                await db.commit()
                
                # Send completion event with details
                await websocket.send_json({
                    "type": "execution_complete",
                    "executionId": str(execution.id),
                    "status": execution.status,
                    "totalSteps": len(nodes),
                    "completedSteps": len(results),
                    "failedSteps": len(failed_steps),
                    "failedStepDetails": failed_steps
                })
            finally:
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
            # Only close if the client is still connected and we haven't closed it
            from starlette.websockets import WebSocketState
            if websocket.client_state != WebSocketState.DISCONNECTED:
                await websocket.close()
        except Exception:
            pass
        
