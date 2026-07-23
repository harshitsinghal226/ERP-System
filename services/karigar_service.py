"""
Karigar service — Business logic for Karigar management.
"""

import logging
from typing import List, Optional

from models.karigar import Karigar
from repositories.karigar_repository import KarigarRepository
from repositories.issue_repository import IssueRepository
from repositories.receive_repository import ReceiveRepository
from utils.helpers import get_balance_status

logger = logging.getLogger(__name__)


class KarigarService:
    """Orchestrates Karigar business operations."""
    
    def __init__(self, karigar_repo: KarigarRepository = None,
                 issue_repo: IssueRepository = None,
                 receive_repo: ReceiveRepository = None):
        self._karigar_repo = karigar_repo or KarigarRepository()
        self._issue_repo = issue_repo or IssueRepository()
        self._receive_repo = receive_repo or ReceiveRepository()
    
    def create(self, karigar: Karigar) -> int:
        """Create a new Karigar with duplicate name check."""
        if self._karigar_repo.name_exists(karigar.karigar_name):
            raise ValueError(f"Karigar '{karigar.karigar_name}' already exists")
        return self._karigar_repo.create(karigar)
    
    def update(self, karigar: Karigar) -> bool:
        """Update Karigar with duplicate name check."""
        if self._karigar_repo.name_exists(karigar.karigar_name, exclude_id=karigar.karigar_id):
            raise ValueError(f"Another Karigar with name '{karigar.karigar_name}' already exists")
        return self._karigar_repo.update(karigar)
    
    def delete(self, karigar_id: int) -> bool:
        """Delete a Karigar (only if no entries exist)."""
        issued = self._issue_repo.get_karigar_total_issued(karigar_id)
        received = self._receive_repo.get_karigar_total_received(karigar_id)
        if issued > 0 or received > 0:
            raise ValueError("Cannot delete Karigar with existing issue/receive entries. Deactivate instead.")
        return self._karigar_repo.delete(karigar_id)
    
    def deactivate(self, karigar_id: int) -> bool:
        return self._karigar_repo.deactivate(karigar_id)
    
    def reactivate(self, karigar_id: int) -> bool:
        return self._karigar_repo.reactivate(karigar_id)
    
    def get_by_id(self, karigar_id: int) -> Optional[Karigar]:
        return self._karigar_repo.get_by_id(karigar_id)
    
    def get_all(self, include_inactive: bool = False) -> List[Karigar]:
        return self._karigar_repo.get_all(include_inactive)
    
    def get_active(self) -> List[Karigar]:
        return self._karigar_repo.get_active()
    
    def search(self, term: str) -> List[Karigar]:
        return self._karigar_repo.search(term)
    
    def get_with_balances(self, include_inactive: bool = False) -> List[Karigar]:
        """Get all Karigars with computed balance fields populated."""
        karigars = self._karigar_repo.get_all(include_inactive)
        
        for k in karigars:
            k.total_issued = self._issue_repo.get_karigar_total_issued(k.karigar_id)
            k.total_received = self._receive_repo.get_karigar_total_received(k.karigar_id)
            k.total_labour = self._receive_repo.get_karigar_total_labour(k.karigar_id)
            k.total_advance = self._issue_repo.get_karigar_total_advance(k.karigar_id)
            k.pending_silver = k.opening_balance + k.total_issued - k.total_received
            k.status = get_balance_status(k.pending_silver)
        
        return karigars
    
    def get_count(self) -> int:
        return self._karigar_repo.get_count()
