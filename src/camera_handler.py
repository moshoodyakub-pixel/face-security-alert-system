"""
Camera Handler Module
Manages webcam/camera operations including frame capture, display, and video feed management.
Optimized for CPU performance with frame skipping and overlay features.
"""

import cv2
import numpy as np
from typing import Optional, Tuple
import time
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class CameraHandler:
    """
    Handles camera operations for the security system.
    Manages frame capture, display, and performance optimizations.
    """
    
    def __init__(
        self,
        camera_source: int = 0,
        width: int = 640,
        height: int = 480,
        fps: int = 30,
        show_video: bool = True,
        show_fps: bool = True
    ):
        """
        Initialize the camera handler.
        
        Args:
            camera_source (int): Camera device index (0 for built-in webcam)
            width (int): Frame width in pixels
            height (int): Frame height in pixels
            fps (int): Target frames per second
            show_video (bool): Display live video feed
            show_fps (bool): Show FPS counter on video
        """
        self.camera_source = camera_source
        self.width = width
        self.height = height
        self.fps = fps
        self.show_video = show_video
        self.show_fps = show_fps
        
        self.camera = None
        self.is_opened = False
        
        # FPS tracking
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0.0
        
        logger.info(
            f"CameraHandler initialized: source={camera_source}, "
            f"resolution={width}x{height}, fps={fps}"
        )
    
    def open(self) -> bool:
        """
        Open the camera and configure settings.
        
        Returns:
            bool: True if camera opened successfully, False otherwise
        """
        try:
            self.camera = cv2.VideoCapture(self.camera_source)
            
            if not self.camera.isOpened():
                logger.error(f"Failed to open camera {self.camera_source}")
                return False
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Verify settings
            actual_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(self.camera.get(cv2.CAP_PROP_FPS))
            
            logger.info(
                f"Camera opened: {actual_width}x{actual_height} @ {actual_fps}fps"
            )
            
            self.is_opened = True
            return True
            
        except Exception as e:
            logger.error(f"Error opening camera: {e}")
            return False
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a single frame from the camera.
        
        Returns:
            Tuple[bool, Optional[np.ndarray]]: (success, frame)
        """
        if not self.is_opened or self.camera is None:
            logger.warning("Camera not opened")
            return False, None
        
        try:
            ret, frame = self.camera.read()
            
            if ret:
                self.frame_count += 1
                self._update_fps()
            
            return ret, frame
            
        except Exception as e:
            logger.error(f"Error reading frame: {e}")
            return False, None
    
    def _update_fps(self):
        """Update FPS calculation (internal method)."""
        elapsed_time = time.time() - self.fps_start_time
        
        if elapsed_time >= 1.0:  # Update every second
            self.current_fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.fps_start_time = time.time()
    
    def draw_fps(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw FPS counter on frame.
        
        Args:
            frame (np.ndarray): Input frame
        
        Returns:
            np.ndarray: Frame with FPS overlay
        """
        if not self.show_fps:
            return frame
        
        fps_text = f"FPS: {self.current_fps:.1f}"
        
        # Draw background for text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        font_thickness = 2
        (text_width, text_height), baseline = cv2.getTextSize(
            fps_text, font, font_scale, font_thickness
        )
        
        cv2.rectangle(
            frame,
            (10, 10),
            (20 + text_width, 20 + text_height),
            (0, 0, 0),
            -1
        )
        
        # Draw FPS text
        cv2.putText(
            frame,
            fps_text,
            (15, 15 + text_height),
            font,
            font_scale,
            (0, 255, 0),
            font_thickness
        )
        
        return frame
    
    def draw_timestamp(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw timestamp on frame.
        
        Args:
            frame (np.ndarray): Input frame
        
        Returns:
            np.ndarray: Frame with timestamp overlay
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        font_thickness = 2
        (text_width, text_height), baseline = cv2.getTextSize(
            timestamp, font, font_scale, font_thickness
        )
        
        # Position at bottom-right
        frame_height, frame_width = frame.shape[:2]
        x = frame_width - text_width - 20
        y = frame_height - 20
        
        # Draw background
        cv2.rectangle(
            frame,
            (x - 5, y - text_height - 5),
            (x + text_width + 5, y + 5),
            (0, 0, 0),
            -1
        )
        
        # Draw timestamp
        cv2.putText(
            frame,
            timestamp,
            (x, y),
            font,
            font_scale,
            (255, 255, 255),
            font_thickness
        )
        
        return frame
    
    def draw_text(
        self,
        frame: np.ndarray,
        text: str,
        position: Tuple[int, int],
        color: Tuple[int, int, int] = (255, 255, 255),
        font_scale: float = 0.6,
        thickness: int = 2,
        with_background: bool = True
    ) -> np.ndarray:
        """
        Draw text on frame with optional background.
        
        Args:
            frame (np.ndarray): Input frame
            text (str): Text to draw
            position (tuple): (x, y) position
            color (tuple): Text color in BGR format
            font_scale (float): Font size
            thickness (int): Text thickness
            with_background (bool): Draw background rectangle
        
        Returns:
            np.ndarray: Frame with text
        """
        font = cv2.FONT_HERSHEY_SIMPLEX
        x, y = position
        
        if with_background:
            (text_width, text_height), baseline = cv2.getTextSize(
                text, font, font_scale, thickness
            )
            
            cv2.rectangle(
                frame,
                (x - 2, y - text_height - 2),
                (x + text_width + 2, y + 2),
                (0, 0, 0),
                -1
            )
        
        cv2.putText(
            frame,
            text,
            (x, y),
            font,
            font_scale,
            color,
            thickness
        )
        
        return frame
    
    def draw_status_message(
        self,
        frame: np.ndarray,
        message: str,
        message_type: str = "info"
    ) -> np.ndarray:
        """
        Draw status message at top of frame.
        
        Args:
            frame (np.ndarray): Input frame
            message (str): Message to display
            message_type (str): Type of message (info, warning, error, success)
        
        Returns:
            np.ndarray: Frame with status message
        """
        # Color based on message type
        colors = {
            'info': (255, 255, 255),
            'warning': (0, 255, 255),
            'error': (0, 0, 255),
            'success': (0, 255, 0)
        }
        color = colors.get(message_type, (255, 255, 255))
        
        frame_height, frame_width = frame.shape[:2]
        
        return self.draw_text(
            frame,
            message,
            (frame_width // 2 - 200, 50),
            color=color,
            font_scale=0.7,
            thickness=2,
            with_background=True
        )
    
    def display_frame(self, frame: np.ndarray, window_name: str = "Face Security System") -> int:
        """
        Display frame in a window.
        
        Args:
            frame (np.ndarray): Frame to display
            window_name (str): Window name
        
        Returns:
            int: Key code pressed (or -1 if no key pressed)
        """
        if not self.show_video:
            return -1
        
        cv2.imshow(window_name, frame)
        return cv2.waitKey(1) & 0xFF
    
    def release(self):
        """Release camera and close windows."""
        if self.camera is not None:
            self.camera.release()
            logger.info("Camera released")
        
        if self.show_video:
            cv2.destroyAllWindows()
            logger.info("Display windows closed")
        
        self.is_opened = False
    
    def is_camera_opened(self) -> bool:
        """
        Check if camera is opened and working.
        
        Returns:
            bool: True if camera is opened
        """
        return self.is_opened and self.camera is not None and self.camera.isOpened()
    
    def get_camera_info(self) -> dict:
        """
        Get camera information and properties.
        
        Returns:
            dict: Camera properties
        """
        if not self.is_camera_opened():
            return {}
        
        return {
            'source': self.camera_source,
            'width': int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': int(self.camera.get(cv2.CAP_PROP_FPS)),
            'current_fps': self.current_fps,
            'backend': self.camera.getBackendName()
        }
    
    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Camera Handler Test")
    print("=" * 50)
    print("Press 'q' to quit")
    print()
    
    # Initialize camera handler
    with CameraHandler(
        camera_source=0,
        width=640,
        height=480,
        fps=30,
        show_video=True,
        show_fps=True
    ) as camera:
        
        # Display camera info
        info = camera.get_camera_info()
        print(f"Camera: {info['width']}x{info['height']} @ {info['fps']}fps")
        print(f"Backend: {info['backend']}")
        print()
        
        # Main loop
        while True:
            ret, frame = camera.read_frame()
            
            if not ret:
                print("Failed to read frame")
                break
            
            # Add overlays
            frame = camera.draw_fps(frame)
            frame = camera.draw_timestamp(frame)
            frame = camera.draw_status_message(frame, "System Active", "success")
            
            # Display
            key = camera.display_frame(frame)
            
            if key == ord('q'):
                print("Quitting...")
                break
    
    print("Camera test complete")
