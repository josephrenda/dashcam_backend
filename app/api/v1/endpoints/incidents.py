"""
Incident API endpoints.
"""
import os
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from math import radians, cos, sin, asin, sqrt
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.incident import Incident, IncidentType, ProcessingStatus
from app.models.vehicle import DetectedVehicle, LicensePlate
from app.schemas.incident import IncidentCreate, IncidentResponse, IncidentList
from app.api.dependencies import get_current_user
from app.tasks.celery_tasks import process_incident_video

router = APIRouter()


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth (in kilometers).
    
    Args:
        lat1, lon1: Latitude and longitude of first point
        lat2, lon2: Latitude and longitude of second point
        
    Returns:
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r


@router.post("/report", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def report_incident(
    video: UploadFile = File(...),
    type: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    timestamp: str = Form(...),
    speed: Optional[float] = Form(None),
    heading: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Report a new incident with video upload.
    
    Args:
        video: Video file upload
        type: Incident type (crash, police, road_rage, hazard, other)
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        timestamp: Incident timestamp (ISO format)
        speed: Optional speed in km/h
        heading: Optional heading in degrees (0-360)
        description: Optional incident description
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Created incident information
        
    Raises:
        HTTPException: If video is too large or invalid
    """
    # Validate incident type
    try:
        incident_type = IncidentType(type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid incident type. Must be one of: {', '.join([t.value for t in IncidentType])}"
        )
    
    # Parse timestamp
    try:
        incident_timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid timestamp format. Use ISO 8601 format."
        )
    
    # Validate video file
    if not video.content_type or not video.content_type.startswith("video/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a video"
        )
    
    # Generate incident ID
    incident_id = str(uuid.uuid4())
    
    # Create storage directory
    storage_dir = os.path.join(settings.VIDEO_STORAGE_PATH, current_user.user_id, incident_id)
    os.makedirs(storage_dir, exist_ok=True)
    
    # Save video file
    video_path = os.path.join(storage_dir, "raw.mp4")
    
    # Read and save video
    video_content = await video.read()
    video_size = len(video_content)
    
    # Check video size (max 500MB)
    max_size_bytes = settings.MAX_VIDEO_SIZE_MB * 1024 * 1024
    if video_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Video size exceeds maximum allowed size of {settings.MAX_VIDEO_SIZE_MB}MB"
        )
    
    with open(video_path, "wb") as f:
        f.write(video_content)
    
    # Create incident record
    incident = Incident(
        incident_id=incident_id,
        user_id=current_user.user_id,
        type=incident_type,
        latitude=latitude,
        longitude=longitude,
        timestamp=incident_timestamp,
        speed=speed,
        heading=heading,
        description=description,
        video_path=video_path,
        video_size=video_size,
        processing_status=ProcessingStatus.PENDING,
        created_at=datetime.utcnow()
    )
    
    db.add(incident)
    db.commit()
    db.refresh(incident)
    
    # Queue Celery task for video processing
    process_incident_video.delay(incident_id)
    
    return incident


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific incident.
    
    Args:
        incident_id: UUID of the incident
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Incident details including processing status and detections
        
    Raises:
        HTTPException: If incident not found
    """
    # Query incident
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    return incident


@router.get("/nearby", response_model=List[IncidentList])
def get_nearby_incidents(
    latitude: float,
    longitude: float,
    radius_km: float = 5.0,
    time_window_hours: int = 24,
    types: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get incidents within a specified radius and time window.
    
    Args:
        latitude: Center point latitude
        longitude: Center point longitude
        radius_km: Search radius in kilometers (default: 5)
        time_window_hours: Time window in hours (default: 24)
        types: Comma-separated incident types to filter (optional)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of nearby incidents sorted by distance
    """
    # Calculate time threshold
    time_threshold = datetime.utcnow() - timedelta(hours=time_window_hours)
    
    # Build query
    query = db.query(Incident).filter(Incident.timestamp >= time_threshold)
    
    # Filter by types if provided
    if types:
        type_list = [t.strip() for t in types.split(",")]
        try:
            incident_types = [IncidentType(t) for t in type_list]
            query = query.filter(Incident.type.in_(incident_types))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid incident type. Must be one of: {', '.join([t.value for t in IncidentType])}"
            )
    
    # Get all incidents (we'll filter by distance in Python)
    incidents = query.all()
    
    # Calculate distances and filter by radius
    nearby_incidents = []
    for incident in incidents:
        distance = haversine_distance(latitude, longitude, incident.latitude, incident.longitude)
        if distance <= radius_km:
            nearby_incidents.append({
                "incident_id": incident.incident_id,
                "type": incident.type,
                "latitude": incident.latitude,
                "longitude": incident.longitude,
                "timestamp": incident.timestamp,
                "distance_km": distance,
                "processing_status": incident.processing_status
            })
    
    # Sort by distance
    nearby_incidents.sort(key=lambda x: x["distance_km"])
    
    return [IncidentList(**inc) for inc in nearby_incidents]


@router.delete("/{incident_id}", status_code=status.HTTP_200_OK)
def delete_incident(
    incident_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an incident (user can only delete their own incidents).
    
    Args:
        incident_id: UUID of the incident to delete
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If incident not found or user doesn't own it
    """
    # Query incident
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Verify user owns the incident
    if incident.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own incidents"
        )
    
    # Delete video file
    if os.path.exists(incident.video_path):
        try:
            # Delete the video file
            os.remove(incident.video_path)
            
            # Try to remove the directory if empty
            video_dir = os.path.dirname(incident.video_path)
            if os.path.exists(video_dir) and not os.listdir(video_dir):
                os.rmdir(video_dir)
        except Exception as e:
            # Log error but continue with database deletion
            print(f"Error deleting video file: {e}")
    
    # Delete incident from database (cascade will delete related records)
    db.delete(incident)
    db.commit()
    
    return {"message": "Incident deleted successfully"}
