"""
Vehicle detection database models.
"""
from sqlalchemy import Column, String, Float, JSON, ForeignKey
from app.core.database import Base


class DetectedVehicle(Base):
    """Detected vehicle model."""
    __tablename__ = "detected_vehicles"
    
    detection_id = Column(String(36), primary_key=True, index=True)
    incident_id = Column(String(36), ForeignKey("incidents.incident_id"), nullable=False)
    vehicle_type = Column(String(50), nullable=False)
    make = Column(String(50), nullable=True)
    model = Column(String(50), nullable=True)
    color = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=False)
    bounding_box = Column(JSON, nullable=False)
    frame_timestamp = Column(Float, nullable=False)


class LicensePlate(Base):
    """License plate detection model."""
    __tablename__ = "license_plates"
    
    plate_id = Column(String(36), primary_key=True, index=True)
    incident_id = Column(String(36), ForeignKey("incidents.incident_id"), nullable=False)
    detection_id = Column(String(36), ForeignKey("detected_vehicles.detection_id"), nullable=True)
    plate_number = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    state_region = Column(String(50), nullable=True)
    country = Column(String(50), nullable=True)
    frame_timestamp = Column(Float, nullable=False)
    bounding_box = Column(JSON, nullable=False)