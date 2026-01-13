"""
User Pydantic schemas.
"""
from typing import Optional, Dict
from pydantic import BaseModel, EmailStr, Field

from app.schemas.auth import UserResponse


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class UserStats(BaseModel):
    """Schema for user statistics."""
    total_incidents: int
    reports_by_type: Dict[str, int]


class UserProfile(BaseModel):
    """Schema for user profile with statistics."""
    user_id: str
    email: str
    username: str
    created_at: str
    stats: UserStats
    
    class Config:
        from_attributes = True
