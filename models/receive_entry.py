"""
Receive Entry domain model.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ReceiveEntry:
    """Represents silver received back from a Karigar."""
    
    receive_id: Optional[int] = None
    receive_date: Optional[datetime] = None
    karigar_id: Optional[int] = None
    item_type_id: Optional[int] = None
    remark: str = ""
    gross_weight: float = 0.0
    labour_weight: float = 0.0
    scrap_weight: float = 0.0   # Auto: Gross - Labour
    net_weight: float = 0.0     # Auto: Gross - Scrap (= Labour)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Joined fields
    karigar_name: str = ""
    item_type_name: str = ""
    
    def calculate_weights(self):
        """Auto-calculate scrap and net weight from gross and labour."""
        self.scrap_weight = max(0, self.gross_weight - self.labour_weight)
        self.net_weight = max(0, self.gross_weight - self.scrap_weight)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ReceiveEntry':
        return cls(
            receive_id=data.get("ReceiveID"),
            receive_date=data.get("ReceiveDate"),
            karigar_id=data.get("KarigarID"),
            item_type_id=data.get("ItemTypeID"),
            remark=data.get("Remark", ""),
            gross_weight=float(data.get("GrossWeight", 0) or 0),
            labour_weight=float(data.get("LabourWeight", 0) or 0),
            scrap_weight=float(data.get("ScrapWeight", 0) or 0),
            net_weight=float(data.get("NetWeight", 0) or 0),
            created_at=data.get("CreatedAt"),
            updated_at=data.get("UpdatedAt"),
            karigar_name=data.get("KarigarName", ""),
            item_type_name=data.get("ItemName", ""),
        )
    
    def to_dict(self) -> dict:
        return {
            "ReceiveDate": self.receive_date,
            "KarigarID": self.karigar_id,
            "ItemTypeID": self.item_type_id,
            "Remark": self.remark,
            "GrossWeight": self.gross_weight,
            "LabourWeight": self.labour_weight,
            "ScrapWeight": self.scrap_weight,
            "NetWeight": self.net_weight,
        }
