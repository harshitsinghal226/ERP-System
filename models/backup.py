"""
Monthly Backup domain model.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MonthlyBackup:
    """Represents a monthly database backup record."""
    
    backup_id: Optional[int] = None
    backup_month: str = ""
    backup_year: str = ""
    backup_path: str = ""
    original_db_path: str = ""
    backup_date: Optional[datetime] = None
    remarks: str = ""
    
    @property
    def display_name(self) -> str:
        return f"{self.backup_month}/{self.backup_year}"
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MonthlyBackup':
        return cls(
            backup_id=data.get("BackupID"),
            backup_month=data.get("BackupMonth", ""),
            backup_year=data.get("BackupYear", ""),
            backup_path=data.get("BackupPath", ""),
            original_db_path=data.get("OriginalDBPath", ""),
            backup_date=data.get("BackupDate"),
            remarks=data.get("Remarks", ""),
        )
