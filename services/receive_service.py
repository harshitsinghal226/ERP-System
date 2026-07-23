"""
Receive Entry service — Business logic for silver receipt with auto-calculation.
"""

import logging
from datetime import datetime
from typing import List, Optional

from models.receive_entry import ReceiveEntry
from repositories.receive_repository import ReceiveRepository
from utils.helpers import parse_date, calculate_scrap, calculate_net_weight

logger = logging.getLogger(__name__)


class ReceiveService:
    """Orchestrates Receive Entry business operations with auto-weight calculation."""
    
    def __init__(self, receive_repo: ReceiveRepository = None):
        self._repo = receive_repo or ReceiveRepository()
    
    def create(self, date_str: str, karigar_id: int, item_type_id: int,
               remark: str, gross_weight: float, labour_weight: float) -> int:
        """
        Create a receive entry with auto-calculated scrap and net weight.
        Scrap = Gross - Labour
        Net = Gross - Scrap (= Labour)
        """
        scrap = calculate_scrap(gross_weight, labour_weight)
        net = calculate_net_weight(gross_weight, scrap)
        
        entry = ReceiveEntry(
            receive_date=parse_date(date_str) or datetime.now(),
            karigar_id=karigar_id,
            item_type_id=item_type_id,
            remark=remark,
            gross_weight=gross_weight,
            labour_weight=labour_weight,
            scrap_weight=scrap,
            net_weight=net,
        )
        return self._repo.create(entry)
    
    def update(self, receive_id: int, date_str: str, karigar_id: int, item_type_id: int,
               remark: str, gross_weight: float, labour_weight: float) -> bool:
        """Update with auto-recalculation of scrap and net."""
        scrap = calculate_scrap(gross_weight, labour_weight)
        net = calculate_net_weight(gross_weight, scrap)
        
        entry = ReceiveEntry(
            receive_id=receive_id,
            receive_date=parse_date(date_str) or datetime.now(),
            karigar_id=karigar_id,
            item_type_id=item_type_id,
            remark=remark,
            gross_weight=gross_weight,
            labour_weight=labour_weight,
            scrap_weight=scrap,
            net_weight=net,
        )
        return self._repo.update(entry)
    
    def delete(self, receive_id: int) -> bool:
        return self._repo.delete(receive_id)
    
    def get_by_id(self, receive_id: int) -> Optional[ReceiveEntry]:
        return self._repo.get_by_id(receive_id)
    
    def get_all_with_details(self) -> List[ReceiveEntry]:
        return self._repo.get_all_with_details()
    
    def get_by_karigar(self, karigar_id: int) -> List[ReceiveEntry]:
        return self._repo.get_by_karigar(karigar_id)
    
    def get_by_date_range(self, start: datetime, end: datetime) -> List[ReceiveEntry]:
        return self._repo.get_by_date_range(start, end)
    
    def get_today_total(self) -> dict:
        return self._repo.get_today_total()
    
    def get_grand_total_received(self) -> float:
        return self._repo.get_grand_total_received()
    
    @staticmethod
    def compute_scrap(gross: float, labour: float) -> float:
        """Static helper for UI real-time calculation."""
        return calculate_scrap(gross, labour)
    
    @staticmethod
    def compute_net(gross: float, scrap: float) -> float:
        """Static helper for UI real-time calculation."""
        return calculate_net_weight(gross, scrap)
