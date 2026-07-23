"""
Application Settings domain model.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AppSettings:
    """Represents a single application setting (key-value pair)."""
    
    setting_id: Optional[int] = None
    setting_key: str = ""
    setting_value: str = ""
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AppSettings':
        return cls(
            setting_id=data.get("SettingID"),
            setting_key=data.get("SettingKey", ""),
            setting_value=data.get("SettingValue", ""),
            updated_at=data.get("UpdatedAt"),
        )
