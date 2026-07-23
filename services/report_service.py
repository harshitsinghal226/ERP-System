"""
Report service — Aggregation and formatting for all report types.
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional

from repositories.report_repository import ReportRepository
from repositories.karigar_repository import KarigarRepository
from utils.helpers import get_balance_status, format_weight, format_currency, format_date

logger = logging.getLogger(__name__)


class ReportService:
    """Generates structured report data ready for display or export."""
    
    def __init__(self, report_repo: ReportRepository = None,
                 karigar_repo: KarigarRepository = None):
        self._report_repo = report_repo or ReportRepository()
        self._karigar_repo = karigar_repo or KarigarRepository()
    
    def get_karigar_ledger(self, karigar_id: int, month: int = None, year: int = None) -> Dict:
        """
        Report 1: Individual Karigar Ledger with running balance.
        
        Returns dict with:
            - karigar: Karigar details
            - entries: List of ledger rows with running balance
            - opening_balance, closing_balance, totals
        """
        karigar = self._karigar_repo.get_by_id(karigar_id)
        if not karigar:
            raise ValueError(f"Karigar ID {karigar_id} not found")
        
        rows = self._report_repo.get_karigar_ledger(karigar_id, month, year)
        
        # Calculate running balance
        running_balance = karigar.opening_balance
        ledger_entries = []
        total_issued = 0
        total_received = 0
        total_labour = 0
        total_advance = 0
        
        for i, row in enumerate(rows):
            issued = float(row.get("IssuedWeight", 0) or 0)
            received = float(row.get("ReceivedWeight", 0) or 0)
            labour = float(row.get("LabourWeight", 0) or 0)
            advance = float(row.get("AdvanceMoney", 0) or 0)
            
            running_balance += issued - received
            
            total_issued += issued
            total_received += received
            total_labour += labour
            total_advance += advance
            
            ledger_entries.append({
                "sn": i + 1,
                "date": format_date(row.get("EntryDate")),
                "karigar_name": row.get("KarigarName", ""),
                "remark": row.get("Remark", ""),
                "received_weight": received,
                "issued_weight": issued,
                "item_type": row.get("ItemType", ""),
                "labour_weight": labour,
                "advance_money": advance,
                "entry_type": row.get("EntryType", ""),
                "running_balance": running_balance,
            })
        
        return {
            "karigar": karigar,
            "entries": ledger_entries,
            "opening_balance": karigar.opening_balance,
            "closing_balance": running_balance,
            "total_issued": total_issued,
            "total_received": total_received,
            "total_labour": total_labour,
            "total_advance": total_advance,
        }
    
    def get_all_karigars_summary(self, month: int = None, year: int = None) -> List[Dict]:
        """
        Report 2: All Karigars Summary — one row per Karigar.
        """
        rows = self._report_repo.get_all_karigars_summary(month, year)
        summary = []
        
        for i, row in enumerate(rows):
            total_issued = float(row.get("TotalIssued", 0) or 0)
            total_received = float(row.get("TotalReceived", 0) or 0)
            total_labour = float(row.get("TotalLabour", 0) or 0)
            total_advance = float(row.get("TotalAdvance", 0) or 0)
            opening = float(row.get("OpeningBalance", 0) or 0)
            closing = opening + total_issued - total_received
            
            summary.append({
                "sn": i + 1,
                "karigar_name": row.get("KarigarName", ""),
                "total_issued": total_issued,
                "total_received": total_received,
                "total_labour": total_labour,
                "total_advance": total_advance,
                "closing_balance": closing,
                "status": get_balance_status(closing),
            })
        
        return summary
    
    def get_date_wise_report(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Report 3: Date-wise entries between selected dates."""
        rows = self._report_repo.get_date_wise_entries(start_date, end_date)
        entries = []
        
        for i, row in enumerate(rows):
            entries.append({
                "sn": i + 1,
                "date": format_date(row.get("EntryDate")),
                "entry_type": "Issue" if row.get("EntryType") == "I" else "Receive",
                "karigar_name": row.get("KarigarName", ""),
                "item_type": row.get("ItemType", ""),
                "remark": row.get("Remark", ""),
                "issued_weight": float(row.get("IssuedWeight", 0) or 0),
                "received_weight": float(row.get("ReceivedWeight", 0) or 0),
                "labour_weight": float(row.get("LabourWeight", 0) or 0),
                "scrap_weight": float(row.get("ScrapWeight", 0) or 0),
                "advance_money": float(row.get("AdvanceMoney", 0) or 0),
            })
        
        return entries
    
    def get_monthly_summary(self, month: int, year: int) -> Dict:
        """Report 4: Monthly Summary with totals."""
        return self._report_repo.get_monthly_summary(month, year)
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics."""
        return self._report_repo.get_dashboard_stats()
