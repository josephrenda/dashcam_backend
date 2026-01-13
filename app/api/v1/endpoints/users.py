"""
User API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.user import User
from app.models.incident import Incident, IncidentType
from app.schemas.user import UserUpdate, UserStats, UserProfile
from app.schemas.auth import UserResponse
from app.schemas.incident import IncidentResponse
from app.api.dependencies import get_current_user

router = APIRouter()


@router.get("/me/incidents", response_model=List[IncidentResponse])
def get_user_incidents(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    type_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's incidents with pagination.
    
    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 10, max: 100)
        type_filter: Optional incident type filter
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Paginated list of user's incidents
    """
    # Build query
    query = db.query(Incident).filter(Incident.user_id == current_user.user_id)
    
    # Apply type filter if provided
    if type_filter:
        try:
            incident_type = IncidentType(type_filter)
            query = query.filter(Incident.type == incident_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid incident type. Must be one of: {', '.join([t.value for t in IncidentType])}"
            )
    
    # Order by most recent first
    query = query.order_by(Incident.created_at.desc())
    
    # Apply pagination
    offset = (page - 1) * per_page
    incidents = query.offset(offset).limit(per_page).all()
    
    return incidents


@router.patch("/me", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile information.
    
    Args:
        user_update: Updated user data (username, email)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If username or email already taken
    """
    # Check if username is being updated and is unique
    if user_update.username is not None:
        existing_user = db.query(User).filter(
            User.username == user_update.username,
            User.user_id != current_user.user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = user_update.username
    
    # Check if email is being updated and is unique
    if user_update.email is not None:
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.user_id != current_user.user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email
    
    # Commit changes
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/me/stats", response_model=UserStats)
def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics about current user's incidents.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        User statistics including total incidents and breakdown by type
    """
    # Get total incident count
    total_incidents = db.query(func.count(Incident.incident_id)).filter(
        Incident.user_id == current_user.user_id
    ).scalar()
    
    # Get incidents by type
    reports_by_type = {}
    for incident_type in IncidentType:
        count = db.query(func.count(Incident.incident_id)).filter(
            Incident.user_id == current_user.user_id,
            Incident.type == incident_type
        ).scalar()
        reports_by_type[incident_type.value] = count
    
    return UserStats(
        total_incidents=total_incidents,
        reports_by_type=reports_by_type
    )
