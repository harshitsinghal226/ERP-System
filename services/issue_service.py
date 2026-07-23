"""
Issue Entry service — Business logic for silver issuance.
"""

import logging
from datetime import datetime
from typing import List, Optional

from models.issue_entry import IssueEntry
from repositories.issue_repository import IssueRepository
from utils.validators import validate_issue_entry
from utils.helpers import parse_date

logger = logging.getLogger(__name__)


class IssueService:
    """Orchestrates Issue Entry business operations."""
    
    def __init__(self, issue_repo: IssueRepository = None):
        self._repo = issue_repo or IssueRepository()
    
    def create(self, date_str: str, karigar_id: int, item_type_id: int,
               remark: str, weight: float, advance_money: float) -> int:
        """Create a new issue entry with validation."""
        entry = IssueEntry(
            issue_date=parse_date(date_str) or datetime.now(),
            karigar_id=karigar_id,
            item_type_id=item_type_id,
            remark=remark,
            weight=weight,
            advance_money=advance_money,
        )
        return self._repo.create(entry)
    
    def update(self, issue_id: int, date_str: str, karigar_id: int, item_type_id: int,
               remark: str, weight: float, advance_money: float) -> bool:
        """Update an existing issue entry."""
        entry = IssueEntry(
            issue_id=issue_id,
            issue_date=parse_date(date_str) or datetime.now(),
            karigar_id=karigar_id,
            item_type_id=item_type_id,
            remark=remark,
            weight=weight,
            advance_money=advance_money,
        )
        return self._repo.update(entry)
    
    def delete(self, issue_id: int) -> bool:
        return self._repo.delete(issue_id)
    
    def get_by_id(self, issue_id: int) -> Optional[IssueEntry]:
        return self._repo.get_by_id(issue_id)
    
    def get_all_with_details(self) -> List[IssueEntry]:
        return self._repo.get_all_with_details()
    
    def get_by_karigar(self, karigar_id: int) -> List[IssueEntry]:
        return self._repo.get_by_karigar(karigar_id)
    
    def get_by_date_range(self, start: datetime, end: datetime) -> List[IssueEntry]:
        return self._repo.get_by_date_range(start, end)
    
    def get_today_total(self) -> dict:
        return self._repo.get_today_total()
    
    def get_grand_total_issued(self) -> float:
        return self._repo.get_grand_total_issued()
    
    def get_grand_total_advance(self) -> float:
        return self._repo.get_grand_total_advance()
