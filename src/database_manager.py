"""
Database Manager Module
Manages the known faces database including loading, saving, adding, and deleting face encodings.
Uses pickle format for storing face image data.
"""

import pickle
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import logging
import shutil
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages the database of known faces for the security system.
    Handles storage, retrieval, and management of face images.
    """
    
    def __init__(
        self,
        known_faces_dir: Path,
        encodings_file: Path,
        min_images_per_person: int = 3,
        max_images_per_person: int = 10
    ):
        """
        Initialize the database manager.
        
        Args:
            known_faces_dir (Path): Directory containing known face images
            encodings_file (Path): Path to save/load face encodings pickle file
            min_images_per_person (int): Minimum images required per person
            max_images_per_person (int): Maximum images to store per person
        """
        self.known_faces_dir = Path(known_faces_dir)
        self.encodings_file = Path(encodings_file)
        self.min_images_per_person = min_images_per_person
        self.max_images_per_person = max_images_per_person
        
        # Ensure directories exist
        self.known_faces_dir.mkdir(parents=True, exist_ok=True)
        self.encodings_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"DatabaseManager initialized: {self.known_faces_dir}")
    
    def load_database(self) -> Dict[str, List[np.ndarray]]:
        """
        Load face database from pickle file.
        
        Returns:
            Dict[str, List[np.ndarray]]: Dictionary mapping names to lists of face images
        """
        if not self.encodings_file.exists():
            logger.info("No existing database found, starting with empty database")
            return {}
        
        try:
            with open(self.encodings_file, 'rb') as f:
                database = pickle.load(f)
            
            logger.info(f"Loaded database with {len(database)} people")
            for name, faces in database.items():
                logger.info(f"  - {name}: {len(faces)} face images")
            
            return database
            
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            return {}
    
    def save_database(self, database: Dict[str, List[np.ndarray]]) -> bool:
        """
        Save face database to pickle file.
        
        Args:
            database (Dict): Database dictionary to save
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create backup of existing database
            if self.encodings_file.exists():
                backup_path = self.encodings_file.with_suffix('.pkl.backup')
                shutil.copy2(self.encodings_file, backup_path)
                logger.debug(f"Created database backup: {backup_path}")
            
            # Save new database
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(database, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            logger.info(f"Database saved successfully with {len(database)} people")
            return True
            
        except Exception as e:
            logger.error(f"Error saving database: {e}")
            return False
    
    def load_person_images(self, person_name: str) -> List[np.ndarray]:
        """
        Load all images for a specific person from the known_faces directory.
        
        Args:
            person_name (str): Name of the person (should match subdirectory name)
        
        Returns:
            List[np.ndarray]: List of face images for this person
        """
        person_dir = self.known_faces_dir / person_name
        
        if not person_dir.exists():
            logger.warning(f"Directory not found for {person_name}: {person_dir}")
            return []
        
        images = []
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        
        # Load all image files
        for img_path in sorted(person_dir.glob('*')):
            if img_path.suffix.lower() in valid_extensions:
                try:
                    # Read image
                    img = cv2.imread(str(img_path))
                    
                    if img is not None:
                        images.append(img)
                        logger.debug(f"Loaded image: {img_path.name}")
                    else:
                        logger.warning(f"Failed to load image: {img_path}")
                        
                except Exception as e:
                    logger.error(f"Error loading {img_path}: {e}")
        
        # Limit number of images
        if len(images) > self.max_images_per_person:
            logger.info(
                f"Using {self.max_images_per_person} of {len(images)} "
                f"images for {person_name}"
            )
            images = images[:self.max_images_per_person]
        
        logger.info(f"Loaded {len(images)} images for {person_name}")
        return images
    
    def build_database(self) -> Dict[str, List[np.ndarray]]:
        """
        Build face database from all subdirectories in known_faces_dir.
        Each subdirectory should be named after the person and contain their face images.
        
        Returns:
            Dict[str, List[np.ndarray]]: Complete face database
        """
        database = {}
        
        # Find all person directories
        person_dirs = [d for d in self.known_faces_dir.iterdir() if d.is_dir()]
        
        if not person_dirs:
            logger.warning(f"No person directories found in {self.known_faces_dir}")
            return database
        
        logger.info(f"Building database from {len(person_dirs)} person directories")
        
        # Load images for each person
        for person_dir in person_dirs:
            person_name = person_dir.name
            
            # Skip hidden directories and special directories
            if person_name.startswith('.') or person_name.startswith('_'):
                continue
            
            images = self.load_person_images(person_name)
            
            # Validate minimum images requirement
            if len(images) < self.min_images_per_person:
                logger.warning(
                    f"Skipping {person_name}: only {len(images)} images "
                    f"(minimum {self.min_images_per_person} required)"
                )
                continue
            
            database[person_name] = images
            logger.info(f"Added {person_name} to database with {len(images)} images")
        
        return database
    
    def add_person(
        self,
        person_name: str,
        images: List[np.ndarray],
        update_if_exists: bool = False
    ) -> bool:
        """
        Add a new person to the database.
        
        Args:
            person_name (str): Name of the person
            images (List[np.ndarray]): List of face images
            update_if_exists (bool): If True, update existing person; if False, fail if exists
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Validate inputs
        if not person_name or not person_name.strip():
            logger.error("Person name cannot be empty")
            return False
        
        if len(images) < self.min_images_per_person:
            logger.error(
                f"Not enough images: {len(images)} provided, "
                f"minimum {self.min_images_per_person} required"
            )
            return False
        
        # Load existing database
        database = self.load_database()
        
        # Check if person already exists
        if person_name in database and not update_if_exists:
            logger.error(f"Person {person_name} already exists in database")
            return False
        
        # Add or update person
        database[person_name] = images[:self.max_images_per_person]
        
        # Save updated database
        if self.save_database(database):
            logger.info(f"Successfully added/updated {person_name} with {len(images)} images")
            return True
        else:
            return False
    
    def delete_person(self, person_name: str) -> bool:
        """
        Delete a person from the database.
        
        Args:
            person_name (str): Name of the person to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        database = self.load_database()
        
        if person_name not in database:
            logger.warning(f"Person {person_name} not found in database")
            return False
        
        # Remove person
        del database[person_name]
        
        # Save updated database
        if self.save_database(database):
            logger.info(f"Successfully deleted {person_name} from database")
            return True
        else:
            return False
    
    def list_people(self) -> List[str]:
        """
        Get list of all people in the database.
        
        Returns:
            List[str]: List of person names
        """
        database = self.load_database()
        return list(database.keys())
    
    def get_person_count(self) -> int:
        """
        Get total number of people in database.
        
        Returns:
            int: Number of people
        """
        database = self.load_database()
        return len(database)
    
    def get_database_stats(self) -> Dict:
        """
        Get statistics about the database.
        
        Returns:
            Dict: Statistics including person count, total images, etc.
        """
        database = self.load_database()
        
        total_images = sum(len(images) for images in database.values())
        
        stats = {
            'num_people': len(database),
            'total_images': total_images,
            'people': {}
        }
        
        for name, images in database.items():
            stats['people'][name] = {
                'num_images': len(images),
                'image_shapes': [img.shape for img in images]
            }
        
        return stats
    
    def validate_database(self) -> List[str]:
        """
        Validate database and return list of issues found.
        
        Returns:
            List[str]: List of validation issues (empty if valid)
        """
        issues = []
        
        if not self.known_faces_dir.exists():
            issues.append(f"Known faces directory does not exist: {self.known_faces_dir}")
            return issues
        
        database = self.load_database()
        
        if not database:
            issues.append("Database is empty")
        
        for name, images in database.items():
            if len(images) < self.min_images_per_person:
                issues.append(
                    f"{name} has only {len(images)} images "
                    f"(minimum {self.min_images_per_person})"
                )
            
            for i, img in enumerate(images):
                if img is None or img.size == 0:
                    issues.append(f"{name}: Invalid image at index {i}")
        
        return issues
    
    def export_database_info(self, output_path: Path) -> bool:
        """
        Export database information to a text file.
        
        Args:
            output_path (Path): Path to save the info file
        
        Returns:
            bool: True if successful
        """
        try:
            stats = self.get_database_stats()
            
            with open(output_path, 'w') as f:
                f.write("Face Database Information\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Database file: {self.encodings_file}\n")
                f.write(f"Known faces directory: {self.known_faces_dir}\n\n")
                f.write(f"Total people: {stats['num_people']}\n")
                f.write(f"Total images: {stats['total_images']}\n\n")
                
                f.write("People in database:\n")
                f.write("-" * 50 + "\n")
                
                for name, info in stats['people'].items():
                    f.write(f"\n{name}:\n")
                    f.write(f"  Number of images: {info['num_images']}\n")
                    f.write(f"  Image shapes: {info['image_shapes']}\n")
            
            logger.info(f"Database info exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting database info: {e}")
            return False


# Example usage
if __name__ == "__main__":
    from config import DATABASE_CONFIG
    
    logging.basicConfig(level=logging.INFO)
    
    # Initialize database manager
    db_manager = DatabaseManager(
        known_faces_dir=DATABASE_CONFIG['known_faces_dir'],
        encodings_file=DATABASE_CONFIG['encodings_file'],
        min_images_per_person=DATABASE_CONFIG['min_images_per_person'],
        max_images_per_person=DATABASE_CONFIG['max_images_per_person']
    )
    
    print("\nDatabase Manager Test")
    print("=" * 50)
    
    # Get stats
    stats = db_manager.get_database_stats()
    print(f"\nPeople in database: {stats['num_people']}")
    print(f"Total images: {stats['total_images']}")
    
    # Validate
    issues = db_manager.validate_database()
    if issues:
        print("\nValidation issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nDatabase validation: OK")
