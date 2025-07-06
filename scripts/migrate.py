"""
Migration script for upgrading from old HttpPro versions.

This script helps migrate from file-based ignore lists to the new
database-driven system.
"""

import os
import sys
import argparse
import logging
from typing import Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import IgnoreHostsDB

logger = logging.getLogger(__name__)

def migrate_ignore_file(file_path: str, db_path: Optional[str] = None, origin: str = "migration"):
    """
    Migrate an old ignore-host.txt file to the new database format.
    
    Args:
        file_path: Path to the old ignore-host.txt file
        db_path: Optional path to the database file
        origin: Origin tag for migrated domains
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    try:
        db = IgnoreHostsDB(db_path)
        count = db.import_from_file(file_path, origin)
        
        logger.info(f"Successfully migrated {count} domains from {file_path}")
        
        # Create backup of original file
        backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(file_path, backup_path)
        logger.info(f"Original file backed up to: {backup_path}")
        
        # Export to new format for compatibility
        db.export_to_file(file_path)
        logger.info(f"Created new format file: {file_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

def main():
    """Main migration script entry point."""
    parser = argparse.ArgumentParser(description="Migrate HttpPro to database format")
    parser.add_argument("--file", required=True, help="Path to ignore-host.txt file to migrate")
    parser.add_argument("--db", help="Database file path (optional)")
    parser.add_argument("--origin", default="migration", help="Origin tag for migrated domains")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting HttpPro migration")
    
    success = migrate_ignore_file(args.file, args.db, args.origin)
    
    if success:
        logger.info("Migration completed successfully")
        print("Migration completed!")
        print("Your old file has been backed up and a new database has been created.")
    else:
        logger.error("Migration failed")
        print("Migration failed. Check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
