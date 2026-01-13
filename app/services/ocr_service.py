"""
OCR service for license plate detection and recognition.
"""
import re
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False


class OCRService:
    """
    OCR service for license plate detection and text recognition.
    """
    
    def __init__(self, languages: List[str] = None):
        """
        Initialize OCR service with EasyOCR.
        
        Args:
            languages: List of language codes (default: ['en'])
        """
        if languages is None:
            languages = ['en']
        
        self.languages = languages
        self.reader = None
        
        if EASYOCR_AVAILABLE:
            try:
                self.reader = easyocr.Reader(languages, gpu=False)
            except Exception as e:
                print(f"Warning: Could not initialize EasyOCR: {e}")
    
    def detect_license_plate(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect license plate regions in a frame.
        This is a placeholder - could use YOLO or other detection model.
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            List of detected plate regions with bounding boxes
        """
        # Placeholder - in production would use a specialized license plate detector
        # For now, we'll try to detect text regions and filter for plate-like patterns
        detections = []
        
        if self.reader is None:
            return detections
        
        try:
            # Use EasyOCR to detect text regions
            results = self.reader.detect(frame)
            
            if results and len(results) > 0:
                # results[0] contains bounding boxes
                # results[1] contains probabilities
                boxes, probs = results
                
                for box, prob in zip(boxes, probs):
                    if prob > 0.5:  # Confidence threshold
                        # Convert box format
                        points = box
                        x_coords = [p[0] for p in points]
                        y_coords = [p[1] for p in points]
                        
                        detection = {
                            "bounding_box": {
                                "x1": int(min(x_coords)),
                                "y1": int(min(y_coords)),
                                "x2": int(max(x_coords)),
                                "y2": int(max(y_coords))
                            },
                            "confidence": float(prob)
                        }
                        detections.append(detection)
        
        except Exception as e:
            print(f"Error during plate detection: {e}")
        
        return detections
    
    def read_plate_text(self, plate_image: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Read text from license plate image using OCR.
        
        Args:
            plate_image: Cropped image of license plate
            
        Returns:
            Dictionary with plate number, confidence, and bounding box, or None
        """
        if self.reader is None or plate_image.size == 0:
            return None
        
        try:
            # Run OCR on the plate image
            results = self.reader.readtext(plate_image)
            
            if not results:
                return None
            
            # Get the best result (highest confidence)
            best_result = max(results, key=lambda x: x[2])
            
            bbox, text, confidence = best_result
            
            # Clean up the text
            text = text.upper().replace(" ", "").replace("-", "")
            
            # Validate that it looks like a plate
            if not self.validate_plate_format(text):
                return None
            
            # Convert bbox format
            points = bbox
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            
            return {
                "plate_number": text,
                "confidence": float(confidence),
                "bounding_box": {
                    "x1": int(min(x_coords)),
                    "y1": int(min(y_coords)),
                    "x2": int(max(x_coords)),
                    "y2": int(max(y_coords))
                }
            }
        
        except Exception as e:
            print(f"Error during plate text reading: {e}")
            return None
    
    def validate_plate_format(self, text: str) -> bool:
        """
        Validate that text matches common license plate formats.
        
        Args:
            text: Text to validate
            
        Returns:
            True if text looks like a license plate, False otherwise
        """
        if not text or len(text) < 2 or len(text) > 10:
            return False
        
        # Check if text contains alphanumeric characters
        if not re.search(r'[A-Z0-9]', text):
            return False
        
        # Should have at least one number
        if not re.search(r'[0-9]', text):
            return False
        
        # Common patterns (can be expanded based on regions)
        patterns = [
            r'^[A-Z]{2,3}[0-9]{3,4}$',  # AB1234 or ABC1234
            r'^[0-9]{3}[A-Z]{3}$',       # 123ABC
            r'^[A-Z0-9]{5,8}$',          # Generic alphanumeric
        ]
        
        for pattern in patterns:
            if re.match(pattern, text):
                return True
        
        # If contains both letters and numbers, accept it
        has_letter = bool(re.search(r'[A-Z]', text))
        has_number = bool(re.search(r'[0-9]', text))
        
        return has_letter and has_number
