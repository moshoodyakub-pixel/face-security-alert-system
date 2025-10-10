"""
Face Detector Module
Handles face detection in images and video frames using DeepFace library.
Optimized for CPU performance with OpenCV backend.
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
from deepface import DeepFace
import logging

# Configure logging
logger = logging.getLogger(__name__)


class FaceDetector:
    """
    Face detection class using DeepFace with OpenCV backend.
    Detects faces in images and returns bounding box coordinates.
    """
    
    def __init__(self, backend: str = "opencv", min_face_size: Tuple[int, int] = (50, 50)):
        """
        Initialize the face detector.
        
        Args:
            backend (str): Detection backend to use. Options: opencv, ssd, dlib, mtcnn, retinaface
            min_face_size (tuple): Minimum face size (width, height) in pixels to detect
        """
        self.backend = backend
        self.min_face_size = min_face_size
        logger.info(f"FaceDetector initialized with backend: {backend}")
    
    def detect_faces(self, image: np.ndarray, enforce_detection: bool = False) -> List[Dict]:
        """
        Detect faces in an image.
        
        Args:
            image (np.ndarray): Input image in BGR format (OpenCV format)
            enforce_detection (bool): If True, raises error when no face detected
        
        Returns:
            List[Dict]: List of detected faces with keys:
                - 'face': Cropped face image
                - 'facial_area': Dict with 'x', 'y', 'w', 'h' coordinates
                - 'confidence': Detection confidence score (0-1)
        """
        try:
            # DeepFace expects RGB format, convert from BGR
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image
            
            # Extract faces using DeepFace
            faces = DeepFace.extract_faces(
                img_path=rgb_image,
                detector_backend=self.backend,
                enforce_detection=enforce_detection,
                align=True  # Align faces for better recognition
            )
            
            # Filter out faces that are too small
            filtered_faces = []
            for face_data in faces:
                facial_area = face_data.get('facial_area', {})
                w = facial_area.get('w', 0)
                h = facial_area.get('h', 0)
                
                if w >= self.min_face_size[0] and h >= self.min_face_size[1]:
                    filtered_faces.append(face_data)
                else:
                    logger.debug(f"Face too small: {w}x{h}, minimum is {self.min_face_size}")
            
            logger.debug(f"Detected {len(filtered_faces)} faces (filtered from {len(faces)})")
            return filtered_faces
            
        except ValueError as e:
            # No face detected
            if enforce_detection:
                logger.warning(f"No face detected in image: {e}")
                raise
            else:
                logger.debug("No face detected in image")
                return []
                
        except Exception as e:
            logger.error(f"Error during face detection: {e}")
            return []
    
    def get_face_coordinates(self, face_data: Dict) -> Tuple[int, int, int, int]:
        """
        Extract bounding box coordinates from face data.
        
        Args:
            face_data (Dict): Face data dictionary from detect_faces()
        
        Returns:
            Tuple[int, int, int, int]: (x, y, w, h) coordinates
        """
        facial_area = face_data.get('facial_area', {})
        x = facial_area.get('x', 0)
        y = facial_area.get('y', 0)
        w = facial_area.get('w', 0)
        h = facial_area.get('h', 0)
        
        return (x, y, w, h)
    
    def draw_face_box(
        self,
        image: np.ndarray,
        x: int,
        y: int,
        w: int,
        h: int,
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2,
        label: str = None,
        confidence: float = None
    ) -> np.ndarray:
        """
        Draw bounding box and label on image.
        
        Args:
            image (np.ndarray): Input image
            x, y, w, h (int): Bounding box coordinates
            color (tuple): Box color in BGR format
            thickness (int): Box line thickness
            label (str): Optional label to display above box
            confidence (float): Optional confidence score to display
        
        Returns:
            np.ndarray: Image with drawn bounding box
        """
        # Draw rectangle
        cv2.rectangle(image, (x, y), (x + w, y + h), color, thickness)
        
        # Draw label if provided
        if label or confidence is not None:
            text_parts = []
            if label:
                text_parts.append(label)
            if confidence is not None:
                text_parts.append(f"{confidence:.1%}")
            
            text = " - ".join(text_parts)
            
            # Calculate text size for background
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_thickness = 2
            (text_width, text_height), baseline = cv2.getTextSize(
                text, font, font_scale, font_thickness
            )
            
            # Draw background rectangle for text
            cv2.rectangle(
                image,
                (x, y - text_height - 10),
                (x + text_width, y),
                color,
                -1  # Filled rectangle
            )
            
            # Draw text
            cv2.putText(
                image,
                text,
                (x, y - 5),
                font,
                font_scale,
                (255, 255, 255),  # White text
                font_thickness
            )
        
        return image
    
    def extract_face_region(self, image: np.ndarray, face_data: Dict) -> Optional[np.ndarray]:
        """
        Extract the face region from an image.
        
        Args:
            image (np.ndarray): Input image
            face_data (Dict): Face data dictionary from detect_faces()
        
        Returns:
            Optional[np.ndarray]: Cropped face image or None if extraction fails
        """
        try:
            x, y, w, h = self.get_face_coordinates(face_data)
            
            # Ensure coordinates are within image bounds
            height, width = image.shape[:2]
            x = max(0, min(x, width - 1))
            y = max(0, min(y, height - 1))
            w = min(w, width - x)
            h = min(h, height - y)
            
            # Extract face region
            face_image = image[y:y+h, x:x+w]
            
            return face_image
            
        except Exception as e:
            logger.error(f"Error extracting face region: {e}")
            return None


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize detector
    detector = FaceDetector(backend="opencv")
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect faces
        faces = detector.detect_faces(frame)
        
        # Draw boxes
        for face_data in faces:
            x, y, w, h = detector.get_face_coordinates(face_data)
            confidence = face_data.get('confidence', 0)
            detector.draw_face_box(frame, x, y, w, h, confidence=confidence)
        
        # Display
        cv2.imshow("Face Detection Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
