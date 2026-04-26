"""
Train Known Faces Script
Build the face database from images in the known_faces directory.
This script processes all person subdirectories and creates face encodings.
"""

import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from src.database_manager import DatabaseManager
from utils.logger import setup_logging
from config import DATABASE_CONFIG, LOGGING_CONFIG


def main():
    """Main function to build face database."""
    print("=" * 60)
    print("Face Security Alert System - Train Known Faces")
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
    
    print(f"Known faces directory: {DATABASE_CONFIG['known_faces_dir']}")
    print(f"Encodings file: {DATABASE_CONFIG['encodings_file']}")
    print(f"Minimum images per person: {DATABASE_CONFIG['min_images_per_person']}")
    print()
    
    # Check if known_faces directory exists and has subdirectories
    known_faces_dir = Path(DATABASE_CONFIG['known_faces_dir'])
    if not known_faces_dir.exists():
        print("❌ Error: Known faces directory does not exist!")
        print(f"   Please create: {known_faces_dir}")
        return 1
    
    person_dirs = [d for d in known_faces_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    if not person_dirs:
        print("❌ Error: No person directories found in known_faces/")
        print()
        print("Please create subdirectories for each person with their photos:")
        print(f"  {known_faces_dir}/person_name/")
        print(f"    ├── photo1.jpg")
        print(f"    ├── photo2.jpg")
        print(f"    └── photo3.jpg")
        print()
        return 1
    
    print(f"Found {len(person_dirs)} person directories:")
    for person_dir in person_dirs:
        image_count = len(list(person_dir.glob('*.jpg')) + list(person_dir.glob('*.png')))
        print(f"  - {person_dir.name}: {image_count} images")
    print()
    
    # Confirm before proceeding
    response = input("Do you want to build the face database? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Operation cancelled.")
        return 0
    
    print()
    print("Building face database...")
    print("This may take a few minutes depending on the number of images.")
    print()
    
    try:
        # Build database with progress bar
        database = db_manager.build_database()
        
        if not database:
            print("❌ Error: Failed to build database (no valid people found)")
            print()
            print("Common issues:")
            print(f"  - Each person needs at least {DATABASE_CONFIG['min_images_per_person']} images")
            print("  - Images must be in .jpg or .png format")
            print("  - Images should contain clear face photos")
            return 1
        
        # Save database
        print("Saving database...")
        if db_manager.save_database(database):
            print()
            print("✅ Database built successfully!")
            print()
            
            # Display statistics
            stats = db_manager.get_database_stats()
            print("Database Statistics:")
            print(f"  Total people: {stats['num_people']}")
            print(f"  Total images: {stats['total_images']}")
            print()
            print("People in database:")
            for name, info in stats['people'].items():
                print(f"  - {name}: {info['num_images']} images")
            print()
            
            # Validate database
            print("Validating database...")
            issues = db_manager.validate_database()
            if issues:
                print("⚠️  Validation warnings:")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print("✅ Database validation passed!")
            print()
            
            # Export database info
            info_file = DATABASE_CONFIG['encodings_file'].parent / "database_info.txt"
            if db_manager.export_database_info(info_file):
                print(f"Database info exported to: {info_file}")
            
            print()
            print("Next steps:")
            print("  1. Test recognition with: python scripts/run_security_system.py")
            print("  2. Or use Jupyter notebook: notebooks/03_test_recognition.ipynb")
            print()
            
            return 0
        else:
            print("❌ Error: Failed to save database")
            return 1
            
    except KeyboardInterrupt:
        print()
        print("Operation interrupted by user")
        return 1
        
    except Exception as e:
        logger.error(f"Error building database: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
