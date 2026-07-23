"""
Settings repository — CRUD operations for Settings table.
"""

import logging
from typing import Dict, Optional

from database.connection import DatabaseConnection
from models.settings import AppSettings
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class SettingsRepository(BaseRepository):
    
    def __init__(self, db: DatabaseConnection = None):
        super().__init__(db)
    
    @property
    def table_name(self) -> str:
        return "Settings"
    
    @property
    def primary_key(self) -> str:
        return "SettingID"
    
    def _map_to_model(self, row: dict) -> AppSettings:
        return AppSettings.from_dict(row)
    
    def get_value(self, key: str, default: str = "") -> str:
        """Get a single setting value by key."""
        query = "SELECT SettingValue FROM Settings WHERE SettingKey = ?"
        result = self._db.execute_query(query, (key,))
        if result:
            return result[0]["SettingValue"] or default
        return default
    
    def set_value(self, key: str, value: str) -> None:
        """Set a setting value (insert or update)."""
        existing = self._db.execute_query(
            "SELECT SettingID FROM Settings WHERE SettingKey = ?", (key,)
        )
        if existing:
            self._db.execute_non_query(
                "UPDATE Settings SET SettingValue = ?, UpdatedAt = NOW() WHERE SettingKey = ?",
                (str(value), key)
            )
        else:
            self._db.execute_non_query(
                "INSERT INTO Settings (SettingKey, SettingValue, UpdatedAt) VALUES (?, ?, NOW())",
                (key, str(value))
            )
    
    def get_all_as_dict(self) -> Dict[str, str]:
        """Get all settings as a key-value dictionary."""
        rows = self._db.execute_query("SELECT SettingKey, SettingValue FROM Settings")
        return {row["SettingKey"]: row["SettingValue"] or "" for row in rows}
    
    def save_all(self, settings: Dict[str, str]) -> None:
        """Save multiple settings at once."""
        for key, value in settings.items():
            self.set_value(key, value)
        logger.info(f"Saved {len(settings)} settings")
