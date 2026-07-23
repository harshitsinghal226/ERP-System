"""
Karigar (Artisan/Maker) domain model.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Karigar:
    """Represents a Karigar (silver artisan/maker)."""
    
    karigar_id: Optional[int] = None
    karigar_name: str = ""
    phone: str = ""
    address: str = ""
    city: str = ""
    opening_balance: float = 0.0
    remark: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Computed fields (not stored in DB)
    total_issued: float = field(default=0.0, repr=False)
    total_received: float = field(default=0.0, repr=False)
    pending_silver: float = field(default=0.0, repr=False)
    total_advance: float = field(default=0.0, repr=False)
    total_labour: float = field(default=0.0, repr=False)
    status: str = field(default="Settled", repr=False)
    
    @property
    def display_name(self) -> str:
        """Name for display in dropdowns and lists."""
        suffix = "" if self.is_active else " (Inactive)"
        return f"{self.karigar_name}{suffix}"
    
    @property
    def closing_balance(self) -> float:
        """Opening + Issued - Received."""
        return self.opening_balance + self.total_issued - self.total_received
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Karigar':
        """Create a Karigar from a database row dictionary."""
        return cls(
            karigar_id=data.get("KarigarID"),
            karigar_name=data.get("KarigarName", ""),
            phone=data.get("Phone", ""),
            address=data.get("Address", ""),
            city=data.get("City", ""),
            opening_balance=float(data.get("OpeningBalance", 0) or 0),
            remark=data.get("Remark", ""),
            is_active=bool(data.get("IsActive", True)),
            created_at=data.get("CreatedAt"),
            updated_at=data.get("UpdatedAt"),
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            "KarigarName": self.karigar_name,
            "Phone": self.phone,
            "Address": self.address,
            "City": self.city,
            "OpeningBalance": self.opening_balance,
            "Remark": self.remark,
            "IsActive": self.is_active,
        }
