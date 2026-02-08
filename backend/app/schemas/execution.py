from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import List, Dict, Any, Optional


class ExecutionResponse(BaseModel):
    id: UUID4
    journey_id: UUID4
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class ExecuteJourneyRequest(BaseModel):
    base_url: str
    session_data: Optional[Dict[str, Any]] = {}
    error_injections: Optional[Dict[str, Any]] = {}
