"""
Database models module initialization.
"""
from app.models.user import User
from app.models.incident import Incident, IncidentType, ProcessingStatus
from app.models.vehicle import DetectedVehicle, LicensePlate

__all__ = [
    "User",
    "Incident",
    "IncidentType",
    "ProcessingStatus",
    "DetectedVehicle",
    "LicensePlate",
]