"""
Face Recognizer Module
Handles face recognition by comparing detected faces against a database of known faces.
Implements alert cooldown and continuous detection threshold logic.
"""

import time
import numpy as np
from typing import Dict, Tuple, Optional
from deepface import DeepFace
import logging
from collections import defaultdict

# Configure logging
logger = logging.getLogger(__name__)


class FaceRecognizer:
    """
    Face recognition class that matches detected faces against known faces database.
    Includes alert cooldown and continuous detection threshold features.
    """
    
    def __init__(
        self,
        model_name: str = "VGG-Face",
        distance_metric: str = "cosine",
        threshold: float = 0.4,
        cooldown_seconds: int = 30,
        detection_threshold_seconds: float = 3.0
    ):
        """
        Initialize the face recognizer.
        
        Args:
            model_name (str): Recognition model name (VGG-Face, Facenet, OpenFace, DeepFace, ArcFace)
            distance_metric (str): Distance metric (cosine, euclidean, euclidean_l2)
            threshold (float): Recognition threshold (lower = stricter)
            cooldown_seconds (int): Minimum seconds between alerts for same person
            detection_threshold_seconds (float): Seconds a person must be detected before alert
        """
        self.model_name = model_name
        self.distance_metric = distance_metric
        self.threshold = threshold
        self.cooldown_seconds = cooldown_seconds
        self.detection_threshold_seconds = detection_threshold_seconds
        
        # Track last alert times for each person
        self.last_alert_times: Dict[str, float] = {}
        
        # Track continuous detection times
        self.detection_start_times: Dict[str, float] = {}
        
        logger.info(
            f"FaceRecognizer initialized: model={model_name}, "
            f"metric={distance_metric}, threshold={threshold}"
        )
    
    def verify_face(
        self,
        face_image: np.ndarray,
        known_face_image: np.ndarray
    ) -> Tuple[bool, float]:
        """
        Verify if two faces match using DeepFace.
        
        Args:
            face_image (np.ndarray): Detected face image
            known_face_image (np.ndarray): Known face image from database
        
        Returns:
            Tuple[bool, float]: (is_match, distance_score)
        """
        try:
            result = DeepFace.verify(
                img1_path=face_image,
                img2_path=known_face_image,
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                enforce_detection=False
            )
            
            distance = result.get('distance', 1.0)
            is_match = result.get('verified', False)
            
            # Apply custom threshold if different from DeepFace's default
            if distance <= self.threshold:
                is_match = True
            else:
                is_match = False
            
            return is_match, distance
            
        except Exception as e:
            logger.error(f"Error during face verification: {e}")
            return False, 1.0
    
    def recognize_face(
        self,
        face_image: np.ndarray,
        known_faces_db: Dict[str, list]
    ) -> Tuple[Optional[str], float, float]:
        """
        Recognize a face by comparing against all known faces.
        
        Args:
            face_image (np.ndarray): Detected face image
            known_faces_db (Dict): Dictionary mapping names to lists of face images
        
        Returns:
            Tuple[Optional[str], float, float]: (name, confidence, distance)
                - name: Matched person's name or None if unknown
                - confidence: Confidence score (0-1, where 1 is highest)
                - distance: Distance score from best match
        """
        if not known_faces_db:
            logger.warning("Known faces database is empty")
            return None, 0.0, 1.0
        
        best_match_name = None
        best_distance = float('inf')
        
        # Compare against all known faces
        for name, face_images in known_faces_db.items():
            for known_face in face_images:
                try:
                    is_match, distance = self.verify_face(face_image, known_face)
                    
                    # Track the best match
                    if distance < best_distance:
                        best_distance = distance
                        if is_match:
                            best_match_name = name
                    
                except Exception as e:
                    logger.error(f"Error comparing with {name}: {e}")
                    continue
        
        # Calculate confidence (inverse of distance, normalized)
        # Lower distance = higher confidence
        if best_distance <= self.threshold:
            confidence = 1.0 - (best_distance / self.threshold)
        else:
            confidence = 0.0
        
        return best_match_name, confidence, best_distance
    
    def should_send_alert(self, person_identifier: str) -> bool:
        """
        Check if enough time has passed since last alert for this person.
        Implements alert cooldown to prevent spam.
        
        Args:
            person_identifier (str): Unique identifier for the person (name or "unknown")
        
        Returns:
            bool: True if alert should be sent, False if in cooldown period
        """
        current_time = time.time()
        
        # Check if person is in cooldown
        if person_identifier in self.last_alert_times:
            time_since_last_alert = current_time - self.last_alert_times[person_identifier]
            
            if time_since_last_alert < self.cooldown_seconds:
                remaining_time = self.cooldown_seconds - time_since_last_alert
                logger.debug(
                    f"Alert cooldown active for {person_identifier}: "
                    f"{remaining_time:.1f}s remaining"
                )
                return False
        
        # Update last alert time
        self.last_alert_times[person_identifier] = current_time
        return True
    
    def update_detection_tracking(self, person_identifier: str) -> bool:
        """
        Track continuous detection time for a person.
        Returns True if person has been detected for longer than threshold.
        
        Args:
            person_identifier (str): Unique identifier for the person
        
        Returns:
            bool: True if detection threshold is met, False otherwise
        """
        current_time = time.time()
        
        # Start tracking if not already tracking
        if person_identifier not in self.detection_start_times:
            self.detection_start_times[person_identifier] = current_time
            logger.debug(f"Started tracking detection for {person_identifier}")
            return False
        
        # Check if detection threshold is met
        detection_duration = current_time - self.detection_start_times[person_identifier]
        
        if detection_duration >= self.detection_threshold_seconds:
            logger.info(
                f"{person_identifier} detected continuously for "
                f"{detection_duration:.1f}s (threshold: {self.detection_threshold_seconds}s)"
            )
            return True
        else:
            logger.debug(
                f"{person_identifier} detection: {detection_duration:.1f}s / "
                f"{self.detection_threshold_seconds}s"
            )
            return False
    
    def reset_detection_tracking(self, person_identifier: str):
        """
        Reset detection tracking for a person (e.g., when they leave the frame).
        
        Args:
            person_identifier (str): Unique identifier for the person
        """
        if person_identifier in self.detection_start_times:
            del self.detection_start_times[person_identifier]
            logger.debug(f"Reset detection tracking for {person_identifier}")
    
    def clear_old_tracking_data(self, max_age_seconds: int = 300):
        """
        Clear tracking data older than specified age to prevent memory leaks.
        
        Args:
            max_age_seconds (int): Maximum age of tracking data in seconds
        """
        current_time = time.time()
        
        # Clear old alert times
        expired_alerts = [
            person for person, alert_time in self.last_alert_times.items()
            if current_time - alert_time > max_age_seconds
        ]
        for person in expired_alerts:
            del self.last_alert_times[person]
        
        # Clear old detection times
        expired_detections = [
            person for person, start_time in self.detection_start_times.items()
            if current_time - start_time > max_age_seconds
        ]
        for person in expired_detections:
            del self.detection_start_times[person]
        
        if expired_alerts or expired_detections:
            logger.debug(
                f"Cleared {len(expired_alerts)} alert records and "
                f"{len(expired_detections)} detection records"
            )
    
    def get_confidence_percentage(self, confidence: float) -> float:
        """
        Convert confidence score to percentage.
        
        Args:
            confidence (float): Confidence score (0-1)
        
        Returns:
            float: Confidence as percentage (0-100)
        """
        return confidence * 100
    
    def reset_cooldowns(self):
        """Reset all cooldown timers (useful for testing)."""
        self.last_alert_times.clear()
        logger.info("All cooldown timers reset")
    
    def reset_all_tracking(self):
        """Reset all tracking data (cooldowns and detection times)."""
        self.last_alert_times.clear()
        self.detection_start_times.clear()
        logger.info("All tracking data reset")


# Example usage
if __name__ == "__main__":
    import cv2
    from pathlib import Path
    
    logging.basicConfig(level=logging.INFO)
    
    # Initialize recognizer
    recognizer = FaceRecognizer(
        model_name="VGG-Face",
        distance_metric="cosine",
        threshold=0.4,
        cooldown_seconds=5,  # Shorter for testing
        detection_threshold_seconds=2.0
    )
    
    print("FaceRecognizer test initialized")
    print(f"Model: {recognizer.model_name}")
    print(f"Threshold: {recognizer.threshold}")
    print(f"Cooldown: {recognizer.cooldown_seconds}s")
