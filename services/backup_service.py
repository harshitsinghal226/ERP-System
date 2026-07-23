"""
Backup service — Monthly database backup and restore operations.
"""

import os
import shutil
import logging
from datetime import datetime
from typing import List, Optional

from config.app_config import DB_PATH, BACKUP_DIR
from models.backup import MonthlyBackup
from repositories.backup_repository import BackupRepository
from database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class BackupService:
    """Handles monthly backup creation, restoration, and management."""
    
    def __init__(self, backup_repo: BackupRepository = None):
        self._repo = backup_repo or BackupRepository()
    
    def create_monthly_backup(self, remarks: str = "") -> MonthlyBackup:
        """
        Create a backup of the current database.
        
        Steps:
        1. Copy current .accdb to backups/YYYY-MM/ folder
        2. Record backup entry in MonthlyBackup table
        
        Returns:
            MonthlyBackup record of the created backup
        """
        now = datetime.now()
        month = f"{now.month:02d}"
        year = str(now.year)
        
        # Create backup directory
        backup_dir = os.path.join(BACKUP_DIR, f"{year}-{month}")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        backup_filename = f"aashu_jewellers_backup_{timestamp}.accdb"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy database file
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Database file not found: {DB_PATH}")
        
        shutil.copy2(DB_PATH, backup_path)
        logger.info(f"Database backed up to: {backup_path}")
        
        # Record in backup table
        backup = MonthlyBackup(
            backup_month=month,
            backup_year=year,
            backup_path=backup_path,
            original_db_path=DB_PATH,
            remarks=remarks or f"Monthly backup — {now.strftime('%B %Y')}",
        )
        backup_id = self._repo.create(backup)
        backup.backup_id = backup_id
        backup.backup_date = now
        
        return backup
    
    def get_all_backups(self) -> List[MonthlyBackup]:
        """Get all backup records sorted by date descending."""
        return self._repo.get_all_sorted()
    
    def delete_backup(self, backup_id: int) -> bool:
        """Delete a backup record and its file."""
        backup = self._repo.get_by_id(backup_id)
        if not backup:
            return False
        
        # Try to delete the file
        backup_obj = MonthlyBackup.from_dict(backup) if isinstance(backup, dict) else backup
        if hasattr(backup_obj, 'backup_path') and os.path.exists(backup_obj.backup_path):
            try:
                os.remove(backup_obj.backup_path)
                logger.info(f"Deleted backup file: {backup_obj.backup_path}")
            except OSError as e:
                logger.warning(f"Could not delete backup file: {e}")
        
        return self._repo.delete(backup_id)
    
    def get_backup_path(self, backup_id: int) -> Optional[str]:
        """Get the file path of a backup."""
        backup = self._repo.get_by_id(backup_id)
        if backup and hasattr(backup, 'backup_path'):
            return backup.backup_path
        return None
    
    def open_backup_database(self, backup_path: str) -> DatabaseConnection:
        """
        Open a backup database for read-only browsing.
        Creates a separate connection to the backup file.
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Create a new connection instance for the backup DB
        backup_db = DatabaseConnection.__new__(DatabaseConnection)
        backup_db._db_path = backup_path
        backup_db._conn_string = None
        backup_db._initialized = True
        
        return backup_db
    
    def get_backup_size(self, backup_path: str) -> str:
        """Get human-readable file size of a backup."""
        if not os.path.exists(backup_path):
            return "N/A"
        
        size_bytes = os.path.getsize(backup_path)
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
