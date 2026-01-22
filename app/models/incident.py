"""
Incident database model.
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Float, DateTime, Text, BigInteger, Enum as SQLEnum, ForeignKey
from app.core.database import Base


class IncidentType(str, Enum):
    """Enum for incident types."""
    CRASH = "crash"
    POLICE = "police"
    ROAD_RAGE = "road_rage"
    HAZARD = "hazard"
    OTHER = "other"


class ProcessingStatus(str, Enum):
    """Enum for processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Incident(Base):
    """Incident model for dashcam incidents."""
    __tablename__ = "incidents"
    
    incident_id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    type = Column(SQLEnum(IncidentType), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    speed = Column(Float, nullable=True)
    heading = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    video_path = Column(String(500), nullable=False)
    video_size = Column(BigInteger, nullable=False)
    processing_status = Column(SQLEnum(ProcessingStatus), nullable=False, default=ProcessingStatus.PENDING)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)