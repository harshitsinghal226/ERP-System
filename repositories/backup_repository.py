"""
Backup repository — CRUD for MonthlyBackup table.
"""

import logging
from typing import List

from database.connection import DatabaseConnection
from models.backup import MonthlyBackup
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class BackupRepository(BaseRepository):
    
    def __init__(self, db: DatabaseConnection = None):
        super().__init__(db)
    
    @property
    def table_name(self) -> str:
        return "MonthlyBackup"
    
    @property
    def primary_key(self) -> str:
        return "BackupID"
    
    def _map_to_model(self, row: dict) -> MonthlyBackup:
        return MonthlyBackup.from_dict(row)
    
    def create(self, backup: MonthlyBackup) -> int:
        query = (
            "INSERT INTO MonthlyBackup "
            "(BackupMonth, BackupYear, BackupPath, OriginalDBPath, BackupDate, Remarks) "
            "VALUES (?, ?, ?, ?, NOW(), ?)"
        )
        params = (
            backup.backup_month, backup.backup_year,
            backup.backup_path, backup.original_db_path,
            backup.remarks,
        )
        return self._db.execute_non_query(query, params)
    
    def get_all_sorted(self) -> List[MonthlyBackup]:
        """Get all backups sorted by date descending."""
        query = "SELECT * FROM MonthlyBackup ORDER BY BackupDate DESC"
        rows = self._db.execute_query(query)
        return [self._map_to_model(row) for row in rows]
    
    def get_by_month_year(self, month: str, year: str) -> List[MonthlyBackup]:
        query = "SELECT * FROM MonthlyBackup WHERE BackupMonth = ? AND BackupYear = ?"
        rows = self._db.execute_query(query, (month, year))
        return [self._map_to_model(row) for row in rows]
