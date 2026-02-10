from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Journey(Base):
    __tablename__ = "journeys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    spec_id = Column(UUID(as_uuid=True), ForeignKey("specs.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    nodes = Column(JSON, nullable=False)  # VueFlow nodes
    edges = Column(JSON, nullable=False)  # VueFlow edges
    generation_method = Column(
        SQLEnum("ai", "manual", name="generation_method"), default="ai"
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="journeys")
    spec = relationship("Spec", back_populates="journeys")
    executions = relationship(
        "Execution", back_populates="journey", cascade="all, delete-orphan"
    )
