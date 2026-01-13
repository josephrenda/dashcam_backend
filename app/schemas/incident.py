"""
Incident Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.models.incident import IncidentType, ProcessingStatus


class IncidentCreate(BaseModel):
    """Schema for creating an incident."""
    type: IncidentType
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timestamp: datetime
    speed: Optional[float] = Field(None, ge=0)
    heading: Optional[float] = Field(None, ge=0, le=360)
    description: Optional[str] = None


class VehicleDetection(BaseModel):
    """Schema for vehicle detection information."""
    detection_id: str
    vehicle_type: str
    make: Optional[str]
    model: Optional[str]
    color: Optional[str]
    confidence: float
    bounding_box: Dict[str, Any]
    frame_timestamp: float
    
    class Config:
        from_attributes = True


class LicensePlateDetection(BaseModel):
    """Schema for license plate detection information."""
    plate_id: str
    plate_number: str
    confidence: float
    state_region: Optional[str]
    country: Optional[str]
    frame_timestamp: float
    bounding_box: Dict[str, Any]
    
    class Config:
        from_attributes = True


class IncidentResponse(BaseModel):
    """Schema for incident response with full details."""
    incident_id: str
    user_id: str
    type: IncidentType
    latitude: float
    longitude: float
    timestamp: datetime
    speed: Optional[float]
    heading: Optional[float]
    description: Optional[str]
    video_path: str
    video_size: int
    processing_status: ProcessingStatus
    created_at: datetime
    detected_vehicles: List[VehicleDetection] = []
    
    class Config:
        from_attributes = True


class IncidentList(BaseModel):
    """Schema for incident list item in nearby incidents."""
    incident_id: str
    type: IncidentType
    latitude: float
    longitude: float
    timestamp: datetime
    distance_km: float
    processing_status: ProcessingStatus
    
    class Config:
        from_attributes = True
