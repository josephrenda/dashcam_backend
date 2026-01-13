"""
Machine learning service for vehicle detection using YOLO.
"""
import os
from typing import List, Dict, Any, Tuple
import numpy as np
from collections import Counter

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class MLDetector:
    """
    Machine learning detector for vehicles using YOLOv8.
    """
    
    # Vehicle classes from COCO dataset
    VEHICLE_CLASSES = {
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck"
    }
    
    def __init__(self, model_path: str = "yolov8n.pt"):
        """
        Initialize ML detector with YOLO model.
        
        Args:
            model_path: Path to YOLO model weights
        """
        self.model_path = model_path
        self.model = None
        
        if YOLO_AVAILABLE:
            try:
                self.model = YOLO(model_path)
            except Exception as e:
                print(f"Warning: Could not load YOLO model: {e}")
    
    def detect_vehicles(self, frame: np.ndarray, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Detect vehicles in a frame.
        
        Args:
            frame: Input frame as numpy array
            confidence_threshold: Minimum confidence score for detections
            
        Returns:
            List of detected vehicles with bounding boxes, confidence, and type
        """
        if self.model is None:
            # Return empty list if model not available
            return []
        
        detections = []
        
        try:
            # Run inference
            results = self.model(frame, verbose=False)
            
            # Process results
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Get class ID and confidence
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    
                    # Check if it's a vehicle and meets confidence threshold
                    if class_id in self.VEHICLE_CLASSES and confidence >= confidence_threshold:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        
                        detection = {
                            "vehicle_type": self.VEHICLE_CLASSES[class_id],
                            "confidence": confidence,
                            "bounding_box": {
                                "x1": int(x1),
                                "y1": int(y1),
                                "x2": int(x2),
                                "y2": int(y2)
                            }
                        }
                        
                        # Detect color from cropped region
                        cropped = frame[int(y1):int(y2), int(x1):int(x2)]
                        if cropped.size > 0:
                            detection["color"] = self.detect_vehicle_color(cropped)
                        
                        detections.append(detection)
        
        except Exception as e:
            print(f"Error during vehicle detection: {e}")
        
        return detections
    
    def classify_vehicle_make_model(self, cropped_image: np.ndarray) -> Tuple[str, str]:
        """
        Classify vehicle make and model (placeholder for future enhancement).
        
        Args:
            cropped_image: Cropped image of vehicle
            
        Returns:
            Tuple of (make, model) or (None, None)
        """
        # Placeholder for future implementation
        # Would require a specialized model trained on vehicle makes/models
        return None, None
    
    def detect_vehicle_color(self, cropped_image: np.ndarray) -> str:
        """
        Detect dominant color of vehicle from cropped image.
        
        Args:
            cropped_image: Cropped image of vehicle
            
        Returns:
            Color name as string
        """
        if cropped_image.size == 0:
            return "unknown"
        
        # Resize for faster processing
        small = cropped_image[::4, ::4]
        
        # Convert to RGB
        if len(small.shape) == 3:
            # Reshape to list of pixels
            pixels = small.reshape(-1, 3)
            
            # Get average color
            avg_color = pixels.mean(axis=0)
            
            # Simple color classification
            r, g, b = avg_color
            
            # Basic color detection logic
            if r > 200 and g > 200 and b > 200:
                return "white"
            elif r < 50 and g < 50 and b < 50:
                return "black"
            elif r > 150 and g < 100 and b < 100:
                return "red"
            elif r < 100 and g > 150 and b < 100:
                return "green"
            elif r < 100 and g < 100 and b > 150:
                return "blue"
            elif r > 150 and g > 150 and b < 100:
                return "yellow"
            elif r > 100 and g > 100 and b > 100:
                return "gray"
            else:
                return "other"
        
        return "unknown"
