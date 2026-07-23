"""
Karigar repository — CRUD operations for Karigars table.
"""

import logging
from typing import List, Optional

from database.connection import DatabaseConnection
from models.karigar import Karigar
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class KarigarRepository(BaseRepository):
    """Data access for Karigars table."""
    
    def __init__(self, db: DatabaseConnection = None):
        super().__init__(db)
    
    @property
    def table_name(self) -> str:
        return "Karigars"
    
    @property
    def primary_key(self) -> str:
        return "KarigarID"
    
    def _map_to_model(self, row: dict) -> Karigar:
        return Karigar.from_dict(row)
    
    def _get_searchable_columns(self) -> List[str]:
        return ["KarigarName", "Phone", "City", "Remark"]
    
    def create(self, karigar: Karigar) -> int:
        """Insert a new Karigar and return the generated ID."""
        query = (
            "INSERT INTO Karigars "
            "(KarigarName, Phone, Address, City, OpeningBalance, Remark, IsActive, CreatedAt, UpdatedAt) "
            "VALUES (?, ?, ?, ?, ?, ?, TRUE, NOW(), NOW())"
        )
        params = (
            karigar.karigar_name,
            karigar.phone,
            karigar.address,
            karigar.city,
            karigar.opening_balance,
            karigar.remark,
        )
        new_id = self._db.execute_non_query(query, params)
        logger.info(f"Created Karigar: {karigar.karigar_name} (ID: {new_id})")
        return new_id
    
    def update(self, karigar: Karigar) -> bool:
        """Update an existing Karigar."""
        query = (
            "UPDATE Karigars SET "
            "KarigarName = ?, Phone = ?, Address = ?, City = ?, "
            "OpeningBalance = ?, Remark = ?, IsActive = ?, UpdatedAt = NOW() "
            "WHERE KarigarID = ?"
        )
        params = (
            karigar.karigar_name,
            karigar.phone,
            karigar.address,
            karigar.city,
            karigar.opening_balance,
            karigar.remark,
            karigar.is_active,
            karigar.karigar_id,
        )
        affected = self._db.execute_non_query(query, params)
        logger.info(f"Updated Karigar ID {karigar.karigar_id}: {karigar.karigar_name}")
        return affected > 0
    
    def deactivate(self, karigar_id: int) -> bool:
        """Soft-delete: set IsActive = FALSE."""
        query = "UPDATE Karigars SET IsActive = FALSE, UpdatedAt = NOW() WHERE KarigarID = ?"
        affected = self._db.execute_non_query(query, (karigar_id,))
        logger.info(f"Deactivated Karigar ID {karigar_id}")
        return affected > 0
    
    def reactivate(self, karigar_id: int) -> bool:
        """Restore a deactivated Karigar."""
        query = "UPDATE Karigars SET IsActive = TRUE, UpdatedAt = NOW() WHERE KarigarID = ?"
        affected = self._db.execute_non_query(query, (karigar_id,))
        logger.info(f"Reactivated Karigar ID {karigar_id}")
        return affected > 0
    
    def get_active(self) -> List[Karigar]:
        """Get only active Karigars (for dropdowns)."""
        query = "SELECT * FROM Karigars WHERE IsActive = TRUE ORDER BY KarigarName"
        rows = self._db.execute_query(query)
        return [self._map_to_model(row) for row in rows]
    
    def get_by_name(self, name: str) -> Optional[Karigar]:
        """Find a Karigar by exact name."""
        query = "SELECT * FROM Karigars WHERE KarigarName = ?"
        rows = self._db.execute_query(query, (name,))
        if rows:
            return self._map_to_model(rows[0])
        return None
    
    def name_exists(self, name: str, exclude_id: int = None) -> bool:
        """Check if a Karigar name already exists (for duplicate detection)."""
        if exclude_id:
            query = "SELECT COUNT(*) AS cnt FROM Karigars WHERE KarigarName = ? AND KarigarID <> ?"
            result = self._db.execute_query(query, (name, exclude_id))
        else:
            query = "SELECT COUNT(*) AS cnt FROM Karigars WHERE KarigarName = ?"
            result = self._db.execute_query(query, (name,))
        return result[0]["cnt"] > 0 if result else False
    
    def get_count(self, active_only: bool = True) -> int:
        """Get total number of Karigars."""
        if active_only:
            return self.count("IsActive = TRUE")
        return self.count()
