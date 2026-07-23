"""
Audit Log domain model.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AuditLog:
    """Represents an audit trail entry for tracking data changes."""
    
    log_id: Optional[int] = None
    user_id: Optional[int] = None
    action: str = ""        # CREATE, UPDATE, DELETE
    table_name: str = ""    # Which table was affected
    record_id: Optional[int] = None
    old_values: str = ""    # JSON string of old values
    new_values: str = ""    # JSON string of new values
    timestamp: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AuditLog':
        return cls(
            log_id=data.get("LogID"),
            user_id=data.get("UserID"),
            action=data.get("Action", ""),
            table_name=data.get("TableName", ""),
            record_id=data.get("RecordID"),
            old_values=data.get("OldValues", ""),
            new_values=data.get("NewValues", ""),
            timestamp=data.get("Timestamp"),
        )
