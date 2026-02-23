from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Spec(Base):
    __tablename__ = "specs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    version = Column(String)
    content = Column(JSON, nullable=False)  # Full OpenAPI spec
    endpoints = Column(JSON, nullable=True)  # Parsed endpoint list
    schemas = Column(JSON, nullable=True)  # Component schemas
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="specs")
    journeys = relationship(
        "Journey", back_populates="spec", cascade="all, delete-orphan"
    )
