"""
Item Type domain model.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ItemType:
    """Represents a silver item type (e.g., Silver Chain Raw, Anklet Raw)."""
    
    item_type_id: Optional[int] = None
    item_name: str = ""
    description: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    @property
    def display_name(self) -> str:
        suffix = "" if self.is_active else " (Disabled)"
        return f"{self.item_name}{suffix}"
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ItemType':
        return cls(
            item_type_id=data.get("ItemTypeID"),
            item_name=data.get("ItemName", ""),
            description=data.get("Description", ""),
            is_active=bool(data.get("IsActive", True)),
            created_at=data.get("CreatedAt"),
        )
    
    def to_dict(self) -> dict:
        return {
            "ItemName": self.item_name,
            "Description": self.description,
            "IsActive": self.is_active,
        }
