"""
Issue Entry domain model.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class IssueEntry:
    """Represents silver issued to a Karigar."""
    
    issue_id: Optional[int] = None
    issue_date: Optional[datetime] = None
    karigar_id: Optional[int] = None
    item_type_id: Optional[int] = None
    remark: str = ""
    weight: float = 0.0
    advance_money: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Joined fields (not stored directly)
    karigar_name: str = ""
    item_type_name: str = ""
    
    @classmethod
    def from_dict(cls, data: dict) -> 'IssueEntry':
        return cls(
            issue_id=data.get("IssueID"),
            issue_date=data.get("IssueDate"),
            karigar_id=data.get("KarigarID"),
            item_type_id=data.get("ItemTypeID"),
            remark=data.get("Remark", ""),
            weight=float(data.get("Weight", 0) or 0),
            advance_money=float(data.get("AdvanceMoney", 0) or 0),
            created_at=data.get("CreatedAt"),
            updated_at=data.get("UpdatedAt"),
            karigar_name=data.get("KarigarName", ""),
            item_type_name=data.get("ItemName", ""),
        )
    
    def to_dict(self) -> dict:
        return {
            "IssueDate": self.issue_date,
            "KarigarID": self.karigar_id,
            "ItemTypeID": self.item_type_id,
            "Remark": self.remark,
            "Weight": self.weight,
            "AdvanceMoney": self.advance_money,
        }
