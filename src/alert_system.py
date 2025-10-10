"""
Alert System Module
Handles sending alerts via Telegram and desktop notifications when unknown faces are detected.
Saves photos of unknown faces with timestamps for security records.
"""

import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from plyer import notification
import traceback

# Configure logging
logger = logging.getLogger(__name__)


class AlertSystem:
    """
    Alert system for sending notifications about security events.
    Supports Telegram messages with photos and Windows desktop notifications.
    """
    
    def __init__(
        self,
        telegram_bot_token: str = "",
        telegram_chat_id: str = "",
        enable_telegram: bool = True,
        enable_desktop: bool = True,
        save_unknown_faces: bool = True,
        unknown_faces_dir: Path = None,
        message_template: str = None
    ):
        """
        Initialize the alert system.
        
        Args:
            telegram_bot_token (str): Telegram bot token from BotFather
            telegram_chat_id (str): Telegram chat ID to send alerts to
            enable_telegram (bool): Enable Telegram notifications
            enable_desktop (bool): Enable desktop notifications
            save_unknown_faces (bool): Save photos of unknown faces
            unknown_faces_dir (Path): Directory to save unknown face photos
            message_template (str): Template for alert messages
        """
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        self.enable_telegram = enable_telegram
        self.enable_desktop = enable_desktop
        self.save_unknown_faces = save_unknown_faces
        self.unknown_faces_dir = Path(unknown_faces_dir) if unknown_faces_dir else Path("data/unknown_faces")
        
        # Default message template
        self.message_template = message_template or (
            "⚠️ *SECURITY ALERT*\n\n"
            "Unknown person detected!\n\n"
            "Time: {timestamp}\n"
            "Confidence: {confidence}%\n\n"
            "Please check the attached photo."
        )
        
        # Initialize Telegram bot if credentials provided
        self.telegram_bot = None
        if self.enable_telegram and self.telegram_bot_token and self.telegram_chat_id:
            try:
                self.telegram_bot = Bot(token=self.telegram_bot_token)
                logger.info("Telegram bot initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
                self.enable_telegram = False
        elif self.enable_telegram:
            logger.warning("Telegram enabled but credentials not provided")
            self.enable_telegram = False
        
        # Ensure unknown faces directory exists
        if self.save_unknown_faces:
            self.unknown_faces_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"AlertSystem initialized: telegram={self.enable_telegram}, desktop={self.enable_desktop}")
    
    def save_unknown_face_photo(
        self,
        face_image: np.ndarray,
        full_frame: Optional[np.ndarray] = None
    ) -> Optional[Path]:
        """
        Save photo of unknown face with timestamp.
        
        Args:
            face_image (np.ndarray): Cropped face image
            full_frame (np.ndarray): Optional full frame for context
        
        Returns:
            Optional[Path]: Path to saved photo or None if failed
        """
        if not self.save_unknown_faces:
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            
            # Save face image
            face_filename = f"unknown_face_{timestamp}.jpg"
            face_path = self.unknown_faces_dir / face_filename
            cv2.imwrite(str(face_path), face_image)
            logger.info(f"Saved unknown face photo: {face_filename}")
            
            # Save full frame if provided
            if full_frame is not None:
                frame_filename = f"unknown_frame_{timestamp}.jpg"
                frame_path = self.unknown_faces_dir / frame_filename
                cv2.imwrite(str(frame_path), full_frame)
                logger.debug(f"Saved full frame: {frame_filename}")
            
            return face_path
            
        except Exception as e:
            logger.error(f"Error saving unknown face photo: {e}")
            return None
    
    def send_desktop_notification(
        self,
        title: str = "Security Alert",
        message: str = "Unknown person detected!",
        timeout: int = 10
    ) -> bool:
        """
        Send Windows desktop notification.
        
        Args:
            title (str): Notification title
            message (str): Notification message
            timeout (int): Display duration in seconds
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enable_desktop:
            return False
        
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Face Security System",
                timeout=timeout
            )
            logger.info("Desktop notification sent")
            return True
            
        except Exception as e:
            logger.error(f"Error sending desktop notification: {e}")
            return False
    
    async def _send_telegram_message_async(
        self,
        message: str,
        photo_path: Optional[Path] = None
    ) -> bool:
        """
        Send Telegram message asynchronously (internal method).
        
        Args:
            message (str): Message text
            photo_path (Path): Optional path to photo attachment
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if photo_path and photo_path.exists():
                # Send photo with caption
                with open(photo_path, 'rb') as photo_file:
                    await self.telegram_bot.send_photo(
                        chat_id=self.telegram_chat_id,
                        photo=photo_file,
                        caption=message,
                        parse_mode='Markdown'
                    )
                logger.info("Telegram alert sent with photo")
            else:
                # Send text message only
                await self.telegram_bot.send_message(
                    chat_id=self.telegram_chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
                logger.info("Telegram alert sent (text only)")
            
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            logger.debug(traceback.format_exc())
            return False
    
    def send_telegram_alert(
        self,
        message: str,
        photo_path: Optional[Path] = None
    ) -> bool:
        """
        Send Telegram alert (synchronous wrapper).
        
        Args:
            message (str): Message text
            photo_path (Path): Optional path to photo attachment
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enable_telegram or not self.telegram_bot:
            logger.debug("Telegram not enabled or not initialized")
            return False
        
        try:
            # Run async function in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self._send_telegram_message_async(message, photo_path)
            )
            loop.close()
            return result
            
        except Exception as e:
            logger.error(f"Error in Telegram alert wrapper: {e}")
            return False
    
    def send_alert(
        self,
        face_image: np.ndarray,
        full_frame: Optional[np.ndarray] = None,
        confidence: float = 0.0,
        additional_info: str = ""
    ) -> bool:
        """
        Send complete alert through all enabled channels.
        
        Args:
            face_image (np.ndarray): Cropped face image
            full_frame (np.ndarray): Optional full frame
            confidence (float): Recognition confidence score (0-1)
            additional_info (str): Additional information to include
        
        Returns:
            bool: True if at least one alert method succeeded
        """
        success = False
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save photo
        photo_path = None
        if self.save_unknown_faces:
            photo_path = self.save_unknown_face_photo(face_image, full_frame)
        
        # Format message
        message = self.message_template.format(
            timestamp=timestamp,
            confidence=f"{confidence * 100:.1f}"
        )
        
        if additional_info:
            message += f"\n\n{additional_info}"
        
        # Send desktop notification
        if self.enable_desktop:
            desktop_success = self.send_desktop_notification(
                title="⚠️ Security Alert",
                message=f"Unknown person detected at {timestamp}"
            )
            success = success or desktop_success
        
        # Send Telegram alert
        if self.enable_telegram:
            telegram_success = self.send_telegram_alert(message, photo_path)
            success = success or telegram_success
        
        if success:
            logger.info(f"Alert sent successfully at {timestamp}")
        else:
            logger.warning(f"All alert methods failed at {timestamp}")
        
        return success
    
    def test_telegram_connection(self) -> bool:
        """
        Test Telegram bot connection.
        
        Returns:
            bool: True if connection successful
        """
        if not self.telegram_bot:
            logger.error("Telegram bot not initialized")
            return False
        
        try:
            # Send test message
            test_message = "🔧 Test message from Face Security Alert System\n\nTelegram connection is working!"
            return self.send_telegram_alert(test_message)
            
        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False
    
    def test_desktop_notification(self) -> bool:
        """
        Test desktop notification.
        
        Returns:
            bool: True if successful
        """
        return self.send_desktop_notification(
            title="Test Notification",
            message="Desktop notifications are working!",
            timeout=5
        )
    
    def get_alert_stats(self) -> dict:
        """
        Get statistics about saved alerts.
        
        Returns:
            dict: Statistics about unknown faces saved
        """
        if not self.unknown_faces_dir.exists():
            return {'total_photos': 0, 'photos': []}
        
        photos = list(self.unknown_faces_dir.glob("unknown_face_*.jpg"))
        
        return {
            'total_photos': len(photos),
            'photos': sorted([p.name for p in photos], reverse=True)[:10],  # Last 10
            'storage_path': str(self.unknown_faces_dir)
        }


# Example usage
if __name__ == "__main__":
    from config import ALERT_CONFIG, TELEGRAM_CONFIG
    
    logging.basicConfig(level=logging.INFO)
    
    # Initialize alert system
    alert_system = AlertSystem(
        telegram_bot_token=TELEGRAM_CONFIG['bot_token'],
        telegram_chat_id=TELEGRAM_CONFIG['chat_id'],
        enable_telegram=ALERT_CONFIG['enable_telegram'],
        enable_desktop=ALERT_CONFIG['enable_desktop'],
        save_unknown_faces=ALERT_CONFIG['save_unknown_faces'],
        unknown_faces_dir=ALERT_CONFIG['unknown_faces_dir'],
        message_template=TELEGRAM_CONFIG['message_template']
    )
    
    print("\nAlert System Test")
    print("=" * 50)
    
    # Test desktop notification
    print("\nTesting desktop notification...")
    alert_system.test_desktop_notification()
    
    # Test Telegram (if configured)
    if alert_system.enable_telegram:
        print("\nTesting Telegram connection...")
        alert_system.test_telegram_connection()
    
    # Show stats
    stats = alert_system.get_alert_stats()
    print(f"\nAlert Statistics:")
    print(f"Total saved photos: {stats['total_photos']}")
