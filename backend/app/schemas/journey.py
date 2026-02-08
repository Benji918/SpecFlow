from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import List, Dict, Any, Optional


class JourneyBase(BaseModel):
    name: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


class JourneyCreate(JourneyBase):
    spec_id: UUID4
    generation_method: Optional[str] = "manual"


class JourneyResponse(JourneyBase):
    id: UUID4
    spec_id: UUID4
    user_id: UUID4
    generation_method: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JourneyUpdate(BaseModel):
    name: Optional[str] = None
    nodes: Optional[List[Dict[str, Any]]] = None
    edges: Optional[List[Dict[str, Any]]] = None


class GenerateJourneysRequest(BaseModel):
    strategy: str = "ai"  # 'ai' or 'manual'
