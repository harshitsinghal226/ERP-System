"""
Abstract base repository defining the CRUD interface.
All concrete repositories inherit from this.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any
import logging

from database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """
    Abstract base class for all repositories.
    Provides common CRUD interface and shared database access.
    """
    
    def __init__(self, db: DatabaseConnection = None):
        self._db = db or DatabaseConnection()
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """Name of the database table."""
        pass
    
    @property
    @abstractmethod
    def primary_key(self) -> str:
        """Name of the primary key column."""
        pass
    
    @abstractmethod
    def _map_to_model(self, row: dict) -> Any:
        """Map a database row dictionary to a domain model instance."""
        pass
    
    def get_by_id(self, record_id: int) -> Optional[Any]:
        """Fetch a single record by its primary key."""
        query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?"
        rows = self._db.execute_query(query, (record_id,))
        if rows:
            return self._map_to_model(rows[0])
        return None
    
    def get_all(self, include_inactive: bool = False) -> List[Any]:
        """Fetch all records, optionally including inactive ones."""
        query = f"SELECT * FROM {self.table_name}"
        
        # Check if table has IsActive column
        if not include_inactive and self._has_active_column():
            query += " WHERE IsActive = TRUE"
        
        query += f" ORDER BY {self.primary_key} DESC"
        rows = self._db.execute_query(query)
        return [self._map_to_model(row) for row in rows]
    
    def delete(self, record_id: int) -> bool:
        """
        Delete a record by its primary key.
        
        Returns:
            True if the record was deleted
        """
        query = f"DELETE FROM {self.table_name} WHERE {self.primary_key} = ?"
        affected = self._db.execute_non_query(query, (record_id,))
        if affected:
            logger.info(f"Deleted {self.table_name} record ID {record_id}")
        return affected > 0
    
    def count(self, where_clause: str = "", params: tuple = None) -> int:
        """Count records, optionally with a WHERE clause."""
        query = f"SELECT COUNT(*) AS cnt FROM {self.table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        result = self._db.execute_query(query, params)
        return result[0]["cnt"] if result else 0
    
    def exists(self, record_id: int) -> bool:
        """Check if a record exists by its primary key."""
        return self.count(f"{self.primary_key} = ?", (record_id,)) > 0
    
    def _has_active_column(self) -> bool:
        """Check if the table has an IsActive column (for soft-delete filtering)."""
        tables_with_active = {"Karigars", "ItemTypes", "Users"}
        return self.table_name in tables_with_active
    
    def search(self, search_term: str, columns: List[str] = None) -> List[Any]:
        """
        Basic text search across specified columns.
        
        Args:
            search_term: Text to search for
            columns: Columns to search in. If None, searches all text columns.
        """
        if not search_term or not search_term.strip():
            return self.get_all()
        
        if not columns:
            columns = self._get_searchable_columns()
        
        conditions = " OR ".join([f"{col} LIKE ?" for col in columns])
        query = f"SELECT * FROM {self.table_name} WHERE ({conditions})"
        params = tuple(f"%{search_term.strip()}%" for _ in columns)
        
        rows = self._db.execute_query(query, params)
        return [self._map_to_model(row) for row in rows]
    
    def _get_searchable_columns(self) -> List[str]:
        """Override to specify which columns are searchable. Default: empty."""
        return []
