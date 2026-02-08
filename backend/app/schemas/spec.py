from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional, Dict, List, Any


class SpecBase(BaseModel):
    name: str


class SpecCreate(SpecBase):
    content: Dict[str, Any]  # OpenAPI spec JSON


class SpecResponse(SpecBase):
    id: UUID4
    version: Optional[str] = None
    endpoints: Optional[List[Dict[str, Any]]] = None
    schemas: Optional[Dict[str, Any]] = None
    uploaded_at: datetime
    user_id: UUID4

    class Config:
        from_attributes = True


class SpecUpdate(BaseModel):
    name: Optional[str] = None
