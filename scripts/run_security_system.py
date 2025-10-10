"""
Run Security System Script
Main 24/7 monitoring script that runs the face recognition security system.
Detects faces, recognizes known people, and sends alerts for unknown faces.
"""

import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import cv2
import time
import logging
from datetime import datetime
from src.face_detector import FaceDetector
from src.face_recognizer import FaceRecognizer
from src.database_manager import DatabaseManager
from src.alert_system import AlertSystem
from src.camera_handler import CameraHandler
from utils.logger import setup_logging
from config import (
    CAMERA_CONFIG,
    DETECTION_CONFIG,
    RECOGNITION_CONFIG,
    ALERT_CONFIG,
    DISPLAY_CONFIG,
    DATABASE_CONFIG,
    TELEGRAM_CONFIG,
    LOGGING_CONFIG,
    PERFORMANCE_CONFIG
)


class SecuritySystem:
    """Main security system class that integrates all components."""
    
    def __init__(self):
        """Initialize all system components."""
        # Set up logging
        self.logger = setup_logging(
            log_dir=LOGGING_CONFIG['log_dir'],
            log_level=LOGGING_CONFIG['log_level'],
            log_to_file=LOGGING_CONFIG['log_to_file'],
            log_to_console=LOGGING_CONFIG['log_to_console']
        )
        
        self.logger.info("Initializing Face Security Alert System...")
        
        # Initialize components
        self.face_detector = FaceDetector(
            backend=DETECTION_CONFIG['backend'],
            min_face_size=DETECTION_CONFIG['min_face_size']
        )
        
        self.face_recognizer = FaceRecognizer(
            model_name=RECOGNITION_CONFIG['model'],
            distance_metric=RECOGNITION_CONFIG['distance_metric'],
            threshold=RECOGNITION_CONFIG['threshold'],
            cooldown_seconds=ALERT_CONFIG['cooldown_seconds'],
            detection_threshold_seconds=ALERT_CONFIG['detection_threshold_seconds']
        )
        
        self.database_manager = DatabaseManager(
            known_faces_dir=DATABASE_CONFIG['known_faces_dir'],
            encodings_file=DATABASE_CONFIG['encodings_file'],
            min_images_per_person=DATABASE_CONFIG['min_images_per_person'],
            max_images_per_person=DATABASE_CONFIG['max_images_per_person']
        )
        
        self.alert_system = AlertSystem(
            telegram_bot_token=TELEGRAM_CONFIG['bot_token'],
            telegram_chat_id=TELEGRAM_CONFIG['chat_id'],
            enable_telegram=ALERT_CONFIG['enable_telegram'],
            enable_desktop=ALERT_CONFIG['enable_desktop'],
            save_unknown_faces=ALERT_CONFIG['save_unknown_faces'],
            unknown_faces_dir=ALERT_CONFIG['unknown_faces_dir'],
            message_template=TELEGRAM_CONFIG['message_template']
        )
        
        self.camera_handler = CameraHandler(
            camera_source=CAMERA_CONFIG['source'],
            width=CAMERA_CONFIG['width'],
            height=CAMERA_CONFIG['height'],
            fps=CAMERA_CONFIG['fps'],
            show_video=DISPLAY_CONFIG['show_video'],
            show_fps=DISPLAY_CONFIG['show_fps']
        )
        
        # Load face database
        self.known_faces_db = {}
        self.frame_counter = 0
        self.running = False
        
        self.logger.info("All components initialized successfully")
    
    def load_database(self) -> bool:
        """Load the known faces database."""
        self.logger.info("Loading face database...")
        self.known_faces_db = self.database_manager.load_database()
        
        if not self.known_faces_db:
            self.logger.error("Face database is empty or could not be loaded")
            return False
        
        stats = self.database_manager.get_database_stats()
        self.logger.info(
            f"Database loaded: {stats['num_people']} people, "
            f"{stats['total_images']} total images"
        )
        return True
    
    def process_frame(self, frame):
        """Process a single frame for face detection and recognition."""
        # Detect faces
        faces = self.face_detector.detect_faces(frame, enforce_detection=False)
        
        if not faces:
            return frame, []
        
        recognized_faces = []
        
        for face_data in faces:
            # Get face coordinates
            x, y, w, h = self.face_detector.get_face_coordinates(face_data)
            
            # Extract face image
            face_image = self.face_detector.extract_face_region(frame, face_data)
            
            if face_image is None:
                continue
            
            # Recognize face
            name, confidence, distance = self.face_recognizer.recognize_face(
                face_image,
                self.known_faces_db
            )
            
            # Determine if face is known or unknown
            if name is not None:
                # Known face
                recognized_faces.append({
                    'name': name,
                    'confidence': confidence,
                    'coordinates': (x, y, w, h),
                    'is_known': True
                })
                
                # Draw green box for known faces
                self.face_detector.draw_face_box(
                    frame, x, y, w, h,
                    color=DISPLAY_CONFIG['known_face_color'],
                    thickness=DISPLAY_CONFIG['box_thickness'],
                    label=name if DISPLAY_CONFIG['show_names'] else None,
                    confidence=confidence if DISPLAY_CONFIG['show_confidence'] else None
                )
            else:
                # Unknown face
                recognized_faces.append({
                    'name': 'Unknown',
                    'confidence': confidence,
                    'coordinates': (x, y, w, h),
                    'is_known': False
                })
                
                # Draw red box for unknown faces
                self.face_detector.draw_face_box(
                    frame, x, y, w, h,
                    color=DISPLAY_CONFIG['unknown_face_color'],
                    thickness=DISPLAY_CONFIG['box_thickness'],
                    label='Unknown' if DISPLAY_CONFIG['show_names'] else None,
                    confidence=confidence if DISPLAY_CONFIG['show_confidence'] else None
                )
                
                # Update detection tracking
                person_id = f"unknown_{x}_{y}"
                if self.face_recognizer.update_detection_tracking(person_id):
                    # Send alert if cooldown period has passed
                    if self.face_recognizer.should_send_alert(person_id):
                        self.logger.warning(f"Unknown person detected at ({x}, {y})")
                        self.alert_system.send_alert(
                            face_image=face_image,
                            full_frame=frame.copy(),
                            confidence=confidence
                        )
        
        return frame, recognized_faces
    
    def run(self):
        """Run the security system main loop."""
        print("=" * 60)
        print("Face Security Alert System - 24/7 Monitoring")
        print("=" * 60)
        print()
        
        # Load database
        if not self.load_database():
            print("❌ Error: Failed to load face database")
            print("   Please run: python scripts/train_known_faces.py")
            return 1
        
        stats = self.database_manager.get_database_stats()
        print(f"✅ Database loaded: {stats['num_people']} people")
        for name in stats['people'].keys():
            print(f"   - {name}")
        print()
        
        # Open camera
        if not self.camera_handler.open():
            print("❌ Error: Failed to open camera")
            return 1
        
        camera_info = self.camera_handler.get_camera_info()
        print(f"✅ Camera opened: {camera_info['width']}x{camera_info['height']}")
        print()
        
        print("System Status:")
        print(f"  Telegram alerts: {'✅ Enabled' if ALERT_CONFIG['enable_telegram'] else '❌ Disabled'}")
        print(f"  Desktop alerts: {'✅ Enabled' if ALERT_CONFIG['enable_desktop'] else '❌ Disabled'}")
        print(f"  Video display: {'✅ Enabled' if DISPLAY_CONFIG['show_video'] else '❌ Disabled'}")
        print()
        print("Press 'q' to quit, 's' to take screenshot")
        print()
        print("Starting monitoring...")
        print("-" * 60)
        
        self.running = True
        self.frame_counter = 0
        
        try:
            while self.running:
                # Read frame
                ret, frame = self.camera_handler.read_frame()
                
                if not ret:
                    self.logger.error("Failed to read frame from camera")
                    break
                
                # Process every Nth frame for performance
                if self.frame_counter % DETECTION_CONFIG['process_every_n_frames'] == 0:
                    frame, recognized_faces = self.process_frame(frame)
                
                self.frame_counter += 1
                
                # Add overlays
                if DISPLAY_CONFIG['show_fps']:
                    frame = self.camera_handler.draw_fps(frame)
                
                if DISPLAY_CONFIG['show_timestamp']:
                    frame = self.camera_handler.draw_timestamp(frame)
                
                # Display status message
                frame = self.camera_handler.draw_status_message(
                    frame,
                    "🔴 MONITORING ACTIVE",
                    "success"
                )
                
                # Display frame
                key = self.camera_handler.display_frame(frame)
                
                # Handle key presses
                if key == ord('q'):
                    self.logger.info("Quit signal received")
                    break
                elif key == ord('s'):
                    # Save screenshot
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    screenshot_path = Path("logs") / f"screenshot_{timestamp}.jpg"
                    cv2.imwrite(str(screenshot_path), frame)
                    self.logger.info(f"Screenshot saved: {screenshot_path}")
                    print(f"Screenshot saved: {screenshot_path}")
                
                # Periodic cleanup of tracking data
                if self.frame_counter % 1000 == 0:
                    self.face_recognizer.clear_old_tracking_data()
                
        except KeyboardInterrupt:
            self.logger.info("System interrupted by user")
            print()
            print("Shutting down...")
            
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}", exc_info=True)
            print(f"❌ Error: {e}")
            return 1
            
        finally:
            # Clean shutdown
            self.camera_handler.release()
            self.logger.info("System shutdown complete")
            print()
            print("System stopped")
            print("=" * 60)
        
        return 0


def main():
    """Main entry point."""
    system = SecuritySystem()
    exit_code = system.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
