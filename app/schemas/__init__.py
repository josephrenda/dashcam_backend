"""
Schemas module initialization.
"""
from app.schemas.auth import UserRegister, UserLogin, Token, TokenRefresh, UserResponse
from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentList,
    VehicleDetection,
    LicensePlateDetection,
)
from app.schemas.user import UserUpdate, UserStats, UserProfile

__all__ = [
    "UserRegister",
    "UserLogin",
    "Token",
    "TokenRefresh",
    "UserResponse",
    "IncidentCreate",
    "IncidentResponse",
    "IncidentList",
    "VehicleDetection",
    "LicensePlateDetection",
    "UserUpdate",
    "UserStats",
    "UserProfile",
]
