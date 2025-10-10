"""
Face Security Alert System - Source Code Package
Contains core modules for face detection, recognition, database management, alerts, and camera handling.
"""

__version__ = "1.0.0"
__author__ = "MIVA Student"
__description__ = "24/7 Face Recognition Security System with Telegram Alerts"

from .face_detector import FaceDetector
from .face_recognizer import FaceRecognizer
from .database_manager import DatabaseManager
from .alert_system import AlertSystem
from .camera_handler import CameraHandler

__all__ = [
    "FaceDetector",
    "FaceRecognizer",
    "DatabaseManager",
    "AlertSystem",
    "CameraHandler",
]
