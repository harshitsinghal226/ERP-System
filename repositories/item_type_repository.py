"""
Item Type repository — CRUD operations for ItemTypes table.
"""

import logging
from typing import List, Optional

from database.connection import DatabaseConnection
from models.item_type import ItemType
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ItemTypeRepository(BaseRepository):
    
    def __init__(self, db: DatabaseConnection = None):
        super().__init__(db)
    
    @property
    def table_name(self) -> str:
        return "ItemTypes"
    
    @property
    def primary_key(self) -> str:
        return "ItemTypeID"
    
    def _map_to_model(self, row: dict) -> ItemType:
        return ItemType.from_dict(row)
    
    def _get_searchable_columns(self) -> List[str]:
        return ["ItemName", "Description"]
    
    def create(self, item_type: ItemType) -> int:
        query = (
            "INSERT INTO ItemTypes (ItemName, Description, IsActive, CreatedAt) "
            "VALUES (?, ?, TRUE, NOW())"
        )
        new_id = self._db.execute_non_query(query, (item_type.item_name, item_type.description))
        logger.info(f"Created ItemType: {item_type.item_name} (ID: {new_id})")
        return new_id
    
    def update(self, item_type: ItemType) -> bool:
        query = (
            "UPDATE ItemTypes SET ItemName = ?, Description = ?, IsActive = ? "
            "WHERE ItemTypeID = ?"
        )
        affected = self._db.execute_non_query(
            query, (item_type.item_name, item_type.description, item_type.is_active, item_type.item_type_id)
        )
        return affected > 0
    
    def deactivate(self, item_type_id: int) -> bool:
        query = "UPDATE ItemTypes SET IsActive = FALSE WHERE ItemTypeID = ?"
        return self._db.execute_non_query(query, (item_type_id,)) > 0
    
    def reactivate(self, item_type_id: int) -> bool:
        query = "UPDATE ItemTypes SET IsActive = TRUE WHERE ItemTypeID = ?"
        return self._db.execute_non_query(query, (item_type_id,)) > 0
    
    def get_active(self) -> List[ItemType]:
        query = "SELECT * FROM ItemTypes WHERE IsActive = TRUE ORDER BY ItemName"
        rows = self._db.execute_query(query)
        return [self._map_to_model(row) for row in rows]
    
    def name_exists(self, name: str, exclude_id: int = None) -> bool:
        if exclude_id:
            query = "SELECT COUNT(*) AS cnt FROM ItemTypes WHERE ItemName = ? AND ItemTypeID <> ?"
            result = self._db.execute_query(query, (name, exclude_id))
        else:
            query = "SELECT COUNT(*) AS cnt FROM ItemTypes WHERE ItemName = ?"
            result = self._db.execute_query(query, (name,))
        return result[0]["cnt"] > 0 if result else False
