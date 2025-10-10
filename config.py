"""
Configuration file for Face Security Alert System.
Contains all system settings and parameters for camera, detection, recognition, and alerts.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Camera settings
CAMERA_CONFIG = {
    "source": 0,  # 0 for built-in webcam, 1 for external USB camera
    "width": 640,  # Resolution width (pixels)
    "height": 480,  # Resolution height (pixels)
    "fps": 30,  # Target frames per second
}

# Detection settings
DETECTION_CONFIG = {
    "backend": "opencv",  # Detection backend: opencv (fastest), ssd, dlib, mtcnn, retinaface
    "process_every_n_frames": 2,  # Process every Nth frame for performance (1 = every frame)
    "min_face_size": (50, 50),  # Minimum face size (width, height) in pixels
    "enforce_detection": False,  # If True, raises error when no face detected; if False, returns None
}

# Recognition settings
RECOGNITION_CONFIG = {
    "model": "VGG-Face",  # Recognition model: VGG-Face (balanced), Facenet, OpenFace, DeepFace, ArcFace
    "distance_metric": "cosine",  # Distance metric: cosine, euclidean, euclidean_l2
    "threshold": 0.4,  # Recognition threshold (lower = stricter, higher = more lenient)
    # Threshold guidelines:
    # - VGG-Face cosine: 0.4 (recommended)
    # - Facenet cosine: 0.4
    # - ArcFace cosine: 0.68
}

# Alert settings
ALERT_CONFIG = {
    "cooldown_seconds": 30,  # Minimum time between alerts for same person (prevents spam)
    "detection_threshold_seconds": 3,  # Person must be detected for this many seconds before alert
    "enable_telegram": True,  # Enable Telegram notifications
    "enable_desktop": True,  # Enable desktop notifications (Windows toast notifications)
    "save_unknown_faces": True,  # Save photos of unknown faces
    "unknown_faces_dir": DATA_DIR / "unknown_faces",
    "max_alerts_per_hour": 20,  # Maximum number of alerts per hour (safety limit)
}

# Display settings
DISPLAY_CONFIG = {
    "show_video": True,  # Show live video feed
    "show_fps": True,  # Display FPS counter
    "show_names": True,  # Display recognized names
    "show_confidence": True,  # Display confidence scores
    "show_timestamp": True,  # Display timestamp on video
    "show_bounding_boxes": True,  # Draw boxes around faces
    "known_face_color": (0, 255, 0),  # Green color for known faces (BGR format)
    "unknown_face_color": (0, 0, 255),  # Red color for unknown faces (BGR format)
    "box_thickness": 2,  # Thickness of bounding box lines
    "font_scale": 0.6,  # Font size for text overlays
    "font_thickness": 2,  # Font thickness for text overlays
}

# Performance settings
PERFORMANCE_CONFIG = {
    "use_gpu": False,  # Use GPU acceleration (requires CUDA-enabled TensorFlow)
    "enable_frame_skip": True,  # Skip frames for better performance
    "max_processing_time_ms": 100,  # Maximum time to process a frame (milliseconds)
    "face_detection_interval": 0.5,  # Minimum time between face detections (seconds)
}

# Database settings
DATABASE_CONFIG = {
    "known_faces_dir": DATA_DIR / "known_faces",
    "encodings_file": DATA_DIR / "encodings" / "face_encodings.pkl",
    "min_images_per_person": 3,  # Minimum number of images required per person
    "max_images_per_person": 10,  # Maximum number of images to use per person
}

# Telegram settings (loaded from environment variables)
TELEGRAM_CONFIG = {
    "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
    "chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
    "send_photos": True,  # Attach photos to Telegram alerts
    "message_template": "⚠️ **SECURITY ALERT**\n\nUnknown person detected!\n\nTime: {timestamp}\nConfidence: {confidence}%\n\nPlease check the attached photo.",
}

# Logging settings
LOGGING_CONFIG = {
    "log_dir": LOGS_DIR,
    "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "log_to_file": True,
    "log_to_console": True,
    "max_log_size_mb": 10,  # Maximum size of a single log file
    "backup_count": 5,  # Number of backup log files to keep
}

# Create necessary directories
def initialize_directories():
    """Create all necessary directories if they don't exist."""
    directories = [
        DATA_DIR,
        DATA_DIR / "known_faces",
        DATA_DIR / "unknown_faces",
        DATA_DIR / "encodings",
        LOGS_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        
        # Create .gitkeep files for empty directories
        gitkeep_path = directory / ".gitkeep"
        if not gitkeep_path.exists() and not any(directory.iterdir()):
            gitkeep_path.touch()

# Initialize directories when config is imported
initialize_directories()

# Validation
def validate_config():
    """Validate configuration settings and warn about potential issues."""
    warnings = []
    
    # Check Telegram credentials
    if ALERT_CONFIG["enable_telegram"]:
        if not TELEGRAM_CONFIG["bot_token"]:
            warnings.append("Telegram bot token not configured. Set TELEGRAM_BOT_TOKEN in .env file.")
        if not TELEGRAM_CONFIG["chat_id"]:
            warnings.append("Telegram chat ID not configured. Set TELEGRAM_CHAT_ID in .env file.")
    
    # Check thresholds
    if RECOGNITION_CONFIG["threshold"] < 0.3:
        warnings.append("Recognition threshold is very strict (< 0.3). May cause many false negatives.")
    elif RECOGNITION_CONFIG["threshold"] > 0.6:
        warnings.append("Recognition threshold is very lenient (> 0.6). May cause false positives.")
    
    # Check performance settings
    if DETECTION_CONFIG["process_every_n_frames"] < 1:
        warnings.append("Invalid frame processing setting. Must be >= 1.")
    
    return warnings

# Print warnings on import
if __name__ == "__main__":
    warnings = validate_config()
    if warnings:
        print("Configuration warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("Configuration validated successfully.")
