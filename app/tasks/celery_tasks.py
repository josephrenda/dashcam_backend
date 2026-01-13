"""
Celery tasks for background video processing.
"""
import os
import time
import uuid
from datetime import datetime

from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.incident import Incident, ProcessingStatus
from app.models.vehicle import DetectedVehicle, LicensePlate
from app.services.video_processor import VideoProcessor
from app.services.ml_detector import MLDetector
from app.services.ocr_service import OCRService


@celery_app.task(name="process_incident_video")
def process_incident_video(incident_id: str):
    """
    Process incident video: extract frames, detect vehicles, and read license plates.
    
    Args:
        incident_id: UUID of the incident to process
    """
    db = SessionLocal()
    start_time = time.time()
    
    try:
        # Get incident from database
        incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
        
        if not incident:
            print(f"Incident {incident_id} not found")
            return
        
        # Update status to processing
        incident.processing_status = ProcessingStatus.PROCESSING
        db.commit()
        
        print(f"Starting processing for incident {incident_id}")
        
        # Initialize services
        video_processor = VideoProcessor()
        ml_detector = MLDetector(settings.YOLO_MODEL)
        ocr_service = OCRService(languages=[settings.OCR_LANGUAGES])
        
        # Extract frames from video
        try:
            frames = video_processor.extract_frames(incident.video_path, fps=1)
            print(f"Extracted {len(frames)} frames from video")
        except Exception as e:
            print(f"Error extracting frames: {e}")
            incident.processing_status = ProcessingStatus.FAILED
            db.commit()
            return
        
        # Process each frame
        for frame_idx, frame in enumerate(frames):
            frame_timestamp = float(frame_idx)
            
            try:
                # Detect vehicles in frame
                vehicle_detections = ml_detector.detect_vehicles(frame)
                
                # Save detected vehicles
                for detection in vehicle_detections:
                    detected_vehicle = DetectedVehicle(
                        detection_id=str(uuid.uuid4()),
                        incident_id=incident_id,
                        vehicle_type=detection["vehicle_type"],
                        make=detection.get("make"),
                        model=detection.get("model"),
                        color=detection.get("color"),
                        confidence=detection["confidence"],
                        bounding_box=detection["bounding_box"],
                        frame_timestamp=frame_timestamp
                    )
                    db.add(detected_vehicle)
                    
                    # Try to detect license plates on vehicle
                    bbox = detection["bounding_box"]
                    try:
                        # Crop vehicle region
                        vehicle_crop = frame[
                            bbox["y1"]:bbox["y2"],
                            bbox["x1"]:bbox["x2"]
                        ]
                        
                        # Run OCR on vehicle region
                        if vehicle_crop.size > 0:
                            plate_result = ocr_service.read_plate_text(vehicle_crop)
                            
                            if plate_result:
                                license_plate = LicensePlate(
                                    plate_id=str(uuid.uuid4()),
                                    incident_id=incident_id,
                                    detection_id=detected_vehicle.detection_id,
                                    plate_number=plate_result["plate_number"],
                                    confidence=plate_result["confidence"],
                                    state_region=None,
                                    country=None,
                                    frame_timestamp=frame_timestamp,
                                    bounding_box=plate_result["bounding_box"]
                                )
                                db.add(license_plate)
                    
                    except Exception as e:
                        print(f"Error detecting plate on vehicle: {e}")
                
                # Also try general license plate detection on full frame
                try:
                    plate_detections = ocr_service.detect_license_plate(frame)
                    
                    for plate_det in plate_detections:
                        bbox = plate_det["bounding_box"]
                        plate_crop = frame[
                            bbox["y1"]:bbox["y2"],
                            bbox["x1"]:bbox["x2"]
                        ]
                        
                        if plate_crop.size > 0:
                            plate_result = ocr_service.read_plate_text(plate_crop)
                            
                            if plate_result:
                                license_plate = LicensePlate(
                                    plate_id=str(uuid.uuid4()),
                                    incident_id=incident_id,
                                    detection_id=None,  # Not associated with specific vehicle
                                    plate_number=plate_result["plate_number"],
                                    confidence=plate_result["confidence"],
                                    state_region=None,
                                    country=None,
                                    frame_timestamp=frame_timestamp,
                                    bounding_box=plate_result["bounding_box"]
                                )
                                db.add(license_plate)
                
                except Exception as e:
                    print(f"Error in general plate detection: {e}")
            
            except Exception as e:
                print(f"Error processing frame {frame_idx}: {e}")
        
        # Commit all detections
        db.commit()
        
        # Generate thumbnail
        try:
            thumbnail_path = os.path.join(
                os.path.dirname(incident.video_path),
                "thumbnail.jpg"
            )
            video_processor.generate_thumbnail(incident.video_path, thumbnail_path)
            print(f"Generated thumbnail at {thumbnail_path}")
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
        
        # Update status to completed
        incident.processing_status = ProcessingStatus.COMPLETED
        db.commit()
        
        processing_time = time.time() - start_time
        print(f"Completed processing incident {incident_id} in {processing_time:.2f} seconds")
    
    except Exception as e:
        print(f"Error processing incident {incident_id}: {e}")
        
        # Update status to failed
        try:
            incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
            if incident:
                incident.processing_status = ProcessingStatus.FAILED
                db.commit()
        except Exception as db_error:
            print(f"Error updating incident status: {db_error}")
    
    finally:
        db.close()
