"""
Add New Person Script
Interactive CLI tool to add a new person to the face database.
Captures photos from webcam or loads from files.
"""

import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import cv2
import time
import logging
from src.database_manager import DatabaseManager
from src.camera_handler import CameraHandler
from utils.logger import setup_logging
from config import DATABASE_CONFIG, CAMERA_CONFIG, LOGGING_CONFIG


def capture_photos_from_webcam(person_name: str, num_photos: int = 5) -> list:
    """
    Capture photos from webcam for a new person.
    
    Args:
        person_name (str): Name of the person
        num_photos (int): Number of photos to capture
    
    Returns:
        list: List of captured images
    """
    print()
    print(f"Starting webcam to capture {num_photos} photos of {person_name}")
    print("=" * 60)
    print()
    print("Instructions:")
    print("  - Position your face in the center of the frame")
    print("  - Press SPACE to capture a photo")
    print("  - Try different angles and expressions")
    print("  - Press 'q' to cancel")
    print()
    
    # Initialize camera
    camera = CameraHandler(
        camera_source=CAMERA_CONFIG['source'],
        width=CAMERA_CONFIG['width'],
        height=CAMERA_CONFIG['height'],
        fps=CAMERA_CONFIG['fps'],
        show_video=True,
        show_fps=True
    )
    
    if not camera.open():
        print("❌ Error: Failed to open camera")
        return []
    
    captured_images = []
    
    try:
        while len(captured_images) < num_photos:
            ret, frame = camera.read_frame()
            
            if not ret:
                print("❌ Error: Failed to read frame")
                break
            
            # Display frame with instructions
            display_frame = frame.copy()
            
            # Draw countdown
            remaining = num_photos - len(captured_images)
            message = f"Photos captured: {len(captured_images)}/{num_photos}"
            
            display_frame = camera.draw_status_message(
                display_frame,
                message,
                "info"
            )
            
            # Draw instruction
            display_frame = camera.draw_text(
                display_frame,
                "Press SPACE to capture",
                (20, display_frame.shape[0] - 30),
                color=(255, 255, 255),
                font_scale=0.7,
                thickness=2
            )
            
            # Display
            key = camera.display_frame(display_frame, "Capture Photos")
            
            if key == ord(' '):
                # Capture photo
                captured_images.append(frame.copy())
                print(f"✅ Photo {len(captured_images)}/{num_photos} captured")
                
                # Brief pause for feedback
                time.sleep(0.3)
                
            elif key == ord('q'):
                print("Capture cancelled")
                break
        
        camera.release()
        
        if len(captured_images) == num_photos:
            print()
            print(f"✅ Successfully captured {num_photos} photos!")
            return captured_images
        else:
            print()
            print(f"⚠️  Only captured {len(captured_images)}/{num_photos} photos")
            if len(captured_images) >= DATABASE_CONFIG['min_images_per_person']:
                response = input("Continue with these photos? (yes/no): ").strip().lower()
                if response in ['yes', 'y']:
                    return captured_images
            return []
            
    except Exception as e:
        print(f"❌ Error during capture: {e}")
        camera.release()
        return []


def load_photos_from_directory(directory_path: Path) -> list:
    """
    Load photos from a directory.
    
    Args:
        directory_path (Path): Path to directory containing photos
    
    Returns:
        list: List of loaded images
    """
    if not directory_path.exists():
        print(f"❌ Error: Directory not found: {directory_path}")
        return []
    
    images = []
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    
    for img_path in directory_path.glob('*'):
        if img_path.suffix.lower() in valid_extensions:
            img = cv2.imread(str(img_path))
            if img is not None:
                images.append(img)
                print(f"✅ Loaded: {img_path.name}")
            else:
                print(f"⚠️  Failed to load: {img_path.name}")
    
    return images


def main():
    """Main function for adding a new person."""
    print("=" * 60)
    print("Face Security Alert System - Add New Person")
    print("=" * 60)
    print()
    
    # Set up logging
    logger = setup_logging(
        log_dir=LOGGING_CONFIG['log_dir'],
        log_level=LOGGING_CONFIG['log_level'],
        log_to_file=LOGGING_CONFIG['log_to_file'],
        log_to_console=LOGGING_CONFIG['log_to_console']
    )
    
    # Initialize database manager
    db_manager = DatabaseManager(
        known_faces_dir=DATABASE_CONFIG['known_faces_dir'],
        encodings_file=DATABASE_CONFIG['encodings_file'],
        min_images_per_person=DATABASE_CONFIG['min_images_per_person'],
        max_images_per_person=DATABASE_CONFIG['max_images_per_person']
    )
    
    # Show current people in database
    people = db_manager.list_people()
    if people:
        print("Current people in database:")
        for person in people:
            print(f"  - {person}")
        print()
    
    # Get person name
    while True:
        person_name = input("Enter person's name: ").strip()
        
        if not person_name:
            print("❌ Name cannot be empty")
            continue
        
        if person_name in people:
            response = input(f"⚠️  {person_name} already exists. Update? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("Operation cancelled")
                return 0
            update_existing = True
            break
        else:
            update_existing = False
            break
    
    print()
    print("How would you like to add photos?")
    print("  1. Capture from webcam")
    print("  2. Load from directory")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    images = []
    
    if choice == '1':
        # Capture from webcam
        num_photos = DATABASE_CONFIG['min_images_per_person']
        try:
            num_input = input(f"Number of photos to capture (default {num_photos}): ").strip()
            if num_input:
                num_photos = int(num_input)
                num_photos = max(
                    DATABASE_CONFIG['min_images_per_person'],
                    min(num_photos, DATABASE_CONFIG['max_images_per_person'])
                )
        except ValueError:
            pass
        
        images = capture_photos_from_webcam(person_name, num_photos)
        
    elif choice == '2':
        # Load from directory
        dir_path = input("Enter directory path: ").strip()
        directory = Path(dir_path)
        print()
        print(f"Loading photos from: {directory}")
        images = load_photos_from_directory(directory)
        
    else:
        print("❌ Invalid choice")
        return 1
    
    if not images:
        print("❌ No photos captured/loaded")
        return 1
    
    print()
    print(f"Total photos: {len(images)}")
    
    if len(images) < DATABASE_CONFIG['min_images_per_person']:
        print(f"❌ Not enough photos. Minimum required: {DATABASE_CONFIG['min_images_per_person']}")
        return 1
    
    # Confirm before adding
    print()
    response = input(f"Add {person_name} to database with {len(images)} photos? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("Operation cancelled")
        return 0
    
    # Add person to database
    print()
    print("Adding to database...")
    
    if db_manager.add_person(person_name, images, update_if_exists=update_existing):
        print(f"✅ Successfully added {person_name} to database!")
        print()
        print("Next steps:")
        print("  1. Rebuild database: python scripts/train_known_faces.py")
        print("  2. Test recognition: python scripts/run_security_system.py")
        print()
        return 0
    else:
        print(f"❌ Failed to add {person_name} to database")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print()
        print("Operation cancelled by user")
        sys.exit(1)
