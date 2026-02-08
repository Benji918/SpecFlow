from sqlalchemy import Column, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Execution(Base):
    __tablename__ = "executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journey_id = Column(UUID(as_uuid=True), ForeignKey("journeys.id"), nullable=False)
    status = Column(
        SQLEnum("running", "completed", "failed", name="execution_status"),
        default="running",
    )
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    results = Column(JSON)  # Array of step results

    # Relationships
    journey = relationship("Journey", back_populates="executions")
