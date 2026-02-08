from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String)
    plan = Column(
        SQLEnum("free", "starter", "team", "pro", name="user_plan"),
        default="free",
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    specs = relationship("Spec", back_populates="user", cascade="all, delete-orphan")
    journeys = relationship(
        "Journey", back_populates="user", cascade="all, delete-orphan"
    )
