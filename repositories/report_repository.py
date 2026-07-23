"""
Report repository — Complex queries for generating reports.
Handles ledger, summary, date-wise, and monthly report data.
"""

import logging
from datetime import datetime
from typing import List, Dict

from database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class ReportRepository:
    """
    Provides specialized queries for report generation.
    Unlike other repositories, this doesn't map to a single table.
    """
    
    def __init__(self, db: DatabaseConnection = None):
        self._db = db or DatabaseConnection()
    
    def get_karigar_ledger(self, karigar_id: int, month: int = None, year: int = None) -> List[Dict]:
        """
        Get combined issue and receive entries for a Karigar.
        Returns entries sorted by date for ledger display.
        
        Each row includes:
            - entry_date, entry_type (I/R), karigar_name, remark
            - issued_weight, received_weight, item_type, labour_weight, advance_money
        """
        date_filter = ""
        params_issue = [karigar_id]
        params_receive = [karigar_id]
        
        if month and year:
            date_filter = " AND MONTH({date_col}) = ? AND YEAR({date_col}) = ?"
            params_issue.extend([month, year])
            params_receive.extend([month, year])
        
        issue_date_filter = date_filter.format(date_col="i.IssueDate")
        receive_date_filter = date_filter.format(date_col="r.ReceiveDate")
        
        # Union query: combine issues and receives into a single ledger
        query = f"""
            SELECT 
                i.IssueDate AS EntryDate,
                'I' AS EntryType,
                k.KarigarName,
                i.Remark,
                0 AS ReceivedWeight,
                i.Weight AS IssuedWeight,
                t.ItemName AS ItemType,
                0 AS LabourWeight,
                i.AdvanceMoney
            FROM (IssueEntries i 
                INNER JOIN Karigars k ON i.KarigarID = k.KarigarID) 
                INNER JOIN ItemTypes t ON i.ItemTypeID = t.ItemTypeID
            WHERE i.KarigarID = ?{issue_date_filter}
            
            UNION ALL
            
            SELECT 
                r.ReceiveDate AS EntryDate,
                'R' AS EntryType,
                k.KarigarName,
                r.Remark,
                r.GrossWeight AS ReceivedWeight,
                0 AS IssuedWeight,
                t.ItemName AS ItemType,
                r.LabourWeight,
                0 AS AdvanceMoney
            FROM (ReceiveEntries r 
                INNER JOIN Karigars k ON r.KarigarID = k.KarigarID) 
                INNER JOIN ItemTypes t ON r.ItemTypeID = t.ItemTypeID
            WHERE r.KarigarID = ?{receive_date_filter}
            
            ORDER BY EntryDate ASC
        """
        
        all_params = tuple(params_issue + params_receive)
        return self._db.execute_query(query, all_params)
    
    def get_all_karigars_summary(self, month: int = None, year: int = None) -> List[Dict]:
        """
        Get summary for all Karigars: total issued, received, labour, advance, balance, status.
        One row per Karigar.
        """
        # Build date filter conditions
        issue_date_cond = ""
        receive_date_cond = ""
        if month and year:
            issue_date_cond = f"AND MONTH(i.IssueDate) = {month} AND YEAR(i.IssueDate) = {year}"
            receive_date_cond = f"AND MONTH(r.ReceiveDate) = {month} AND YEAR(r.ReceiveDate) = {year}"
        
        query = f"""
            SELECT 
                k.KarigarID,
                k.KarigarName,
                k.OpeningBalance,
                k.IsActive,
                IIF(issued.TotalIssued IS NULL, 0, issued.TotalIssued) AS TotalIssued,
                IIF(received.TotalReceived IS NULL, 0, received.TotalReceived) AS TotalReceived,
                IIF(received.TotalLabour IS NULL, 0, received.TotalLabour) AS TotalLabour,
                IIF(issued.TotalAdvance IS NULL, 0, issued.TotalAdvance) AS TotalAdvance
            FROM ((Karigars k
            LEFT JOIN (
                SELECT KarigarID, SUM(Weight) AS TotalIssued, SUM(AdvanceMoney) AS TotalAdvance
                FROM IssueEntries i
                WHERE 1=1 {issue_date_cond}
                GROUP BY KarigarID
            ) AS issued ON k.KarigarID = issued.KarigarID)
            LEFT JOIN (
                SELECT KarigarID, SUM(GrossWeight) AS TotalReceived, SUM(LabourWeight) AS TotalLabour
                FROM ReceiveEntries r
                WHERE 1=1 {receive_date_cond}
                GROUP BY KarigarID
            ) AS received ON k.KarigarID = received.KarigarID)
            WHERE k.IsActive = -1
            ORDER BY k.KarigarName
        """
        
        return self._db.execute_query(query)
    
    def get_date_wise_entries(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Get all issue and receive entries between two dates.
        Combined and sorted by date.
        """
        query = """
            SELECT 
                i.IssueDate AS EntryDate,
                'I' AS EntryType,
                k.KarigarName,
                t.ItemName AS ItemType,
                i.Remark,
                i.Weight AS IssuedWeight,
                0 AS ReceivedWeight,
                0 AS LabourWeight,
                0 AS ScrapWeight,
                i.AdvanceMoney
            FROM (IssueEntries i 
                INNER JOIN Karigars k ON i.KarigarID = k.KarigarID) 
                INNER JOIN ItemTypes t ON i.ItemTypeID = t.ItemTypeID
            WHERE i.IssueDate >= ? AND i.IssueDate <= ?
            
            UNION ALL
            
            SELECT 
                r.ReceiveDate AS EntryDate,
                'R' AS EntryType,
                k.KarigarName,
                t.ItemName AS ItemType,
                r.Remark,
                0 AS IssuedWeight,
                r.GrossWeight AS ReceivedWeight,
                r.LabourWeight,
                r.ScrapWeight,
                0 AS AdvanceMoney
            FROM (ReceiveEntries r 
                INNER JOIN Karigars k ON r.KarigarID = k.KarigarID) 
                INNER JOIN ItemTypes t ON r.ItemTypeID = t.ItemTypeID
            WHERE r.ReceiveDate >= ? AND r.ReceiveDate <= ?
            
            ORDER BY EntryDate ASC
        """
        return self._db.execute_query(query, (start_date, end_date, start_date, end_date))
    
    def get_monthly_summary(self, month: int, year: int) -> Dict:
        """
        Get monthly totals: issued, received, labour, scrap, advance.
        """
        issue_query = """
            SELECT 
                IIF(SUM(Weight) IS NULL, 0, SUM(Weight)) AS TotalIssued,
                IIF(SUM(AdvanceMoney) IS NULL, 0, SUM(AdvanceMoney)) AS TotalAdvance,
                COUNT(*) AS IssueCount
            FROM IssueEntries
            WHERE MONTH(IssueDate) = ? AND YEAR(IssueDate) = ?
        """
        
        receive_query = """
            SELECT 
                IIF(SUM(GrossWeight) IS NULL, 0, SUM(GrossWeight)) AS TotalReceived,
                IIF(SUM(LabourWeight) IS NULL, 0, SUM(LabourWeight)) AS TotalLabour,
                IIF(SUM(ScrapWeight) IS NULL, 0, SUM(ScrapWeight)) AS TotalScrap,
                COUNT(*) AS ReceiveCount
            FROM ReceiveEntries
            WHERE MONTH(ReceiveDate) = ? AND YEAR(ReceiveDate) = ?
        """
        
        issue_result = self._db.execute_query(issue_query, (month, year))
        receive_result = self._db.execute_query(receive_query, (month, year))
        
        summary = {
            "month": month,
            "year": year,
            "total_issued": 0,
            "total_advance": 0,
            "issue_count": 0,
            "total_received": 0,
            "total_labour": 0,
            "total_scrap": 0,
            "receive_count": 0,
            "closing_balance": 0,
        }
        
        if issue_result:
            summary["total_issued"] = float(issue_result[0].get("TotalIssued", 0) or 0)
            summary["total_advance"] = float(issue_result[0].get("TotalAdvance", 0) or 0)
            summary["issue_count"] = int(issue_result[0].get("IssueCount", 0) or 0)
        
        if receive_result:
            summary["total_received"] = float(receive_result[0].get("TotalReceived", 0) or 0)
            summary["total_labour"] = float(receive_result[0].get("TotalLabour", 0) or 0)
            summary["total_scrap"] = float(receive_result[0].get("TotalScrap", 0) or 0)
            summary["receive_count"] = int(receive_result[0].get("ReceiveCount", 0) or 0)
        
        summary["closing_balance"] = summary["total_issued"] - summary["total_received"]
        
        return summary
    
    def get_dashboard_stats(self) -> Dict:
        """Get all statistics needed for the dashboard."""
        stats = {}
        
        # Karigar count
        result = self._db.execute_query("SELECT COUNT(*) AS cnt FROM Karigars WHERE IsActive = TRUE")
        stats["total_karigars"] = result[0]["cnt"] if result else 0
        
        # Total issued
        result = self._db.execute_query(
            "SELECT IIF(SUM(Weight) IS NULL, 0, SUM(Weight)) AS total FROM IssueEntries"
        )
        stats["total_issued"] = float(result[0]["total"]) if result else 0
        
        # Total received
        result = self._db.execute_query(
            "SELECT IIF(SUM(GrossWeight) IS NULL, 0, SUM(GrossWeight)) AS total FROM ReceiveEntries"
        )
        stats["total_received"] = float(result[0]["total"]) if result else 0
        
        # Pending
        stats["pending_silver"] = stats["total_issued"] - stats["total_received"]
        
        # Total advance
        result = self._db.execute_query(
            "SELECT IIF(SUM(AdvanceMoney) IS NULL, 0, SUM(AdvanceMoney)) AS total FROM IssueEntries"
        )
        stats["total_advance"] = float(result[0]["total"]) if result else 0
        
        # Today's stats
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today.replace(hour=23, minute=59, second=59)
        
        result = self._db.execute_query(
            "SELECT IIF(SUM(Weight) IS NULL, 0, SUM(Weight)) AS total FROM IssueEntries "
            "WHERE IssueDate >= ? AND IssueDate < ?",
            (today, tomorrow)
        )
        stats["today_issued"] = float(result[0]["total"]) if result else 0
        
        result = self._db.execute_query(
            "SELECT IIF(SUM(GrossWeight) IS NULL, 0, SUM(GrossWeight)) AS total FROM ReceiveEntries "
            "WHERE ReceiveDate >= ? AND ReceiveDate < ?",
            (today, tomorrow)
        )
        stats["today_received"] = float(result[0]["total"]) if result else 0
        
        return stats
