"""
Search service — Multi-criteria search across Issue and Receive entries.
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional

from database.connection import DatabaseConnection
from utils.helpers import parse_date

logger = logging.getLogger(__name__)


class SearchService:
    """Provides unified search across Issue and Receive entries."""
    
    def __init__(self, db: DatabaseConnection = None):
        self._db = db or DatabaseConnection()
    
    def search(self, karigar_name: str = "", item_type: str = "",
               date_from: str = "", date_to: str = "",
               month: int = None, year: int = None,
               entry_type: str = "", weight_min: float = None,
               weight_max: float = None, remark: str = "") -> List[Dict]:
        """
        Multi-criteria search returning combined issue and receive results.
        
        Args:
            karigar_name: Partial Karigar name match
            item_type: Partial Item Type name match
            date_from/date_to: Date range (DD-MM-YYYY)
            month/year: Specific month/year filter
            entry_type: 'I' for issues, 'R' for receives, '' for both
            weight_min/weight_max: Weight range filter
            remark: Partial remark match
        
        Returns:
            List of result dicts with unified columns
        """
        results = []
        
        # Search Issues
        if entry_type != "R":
            results.extend(self._search_issues(
                karigar_name, item_type, date_from, date_to,
                month, year, weight_min, weight_max, remark
            ))
        
        # Search Receives
        if entry_type != "I":
            results.extend(self._search_receives(
                karigar_name, item_type, date_from, date_to,
                month, year, weight_min, weight_max, remark
            ))
        
        # Sort by date
        results.sort(key=lambda x: x.get("entry_date") or datetime.min)
        return results
    
    def _search_issues(self, karigar_name, item_type, date_from, date_to,
                       month, year, weight_min, weight_max, remark) -> List[Dict]:
        """Search in IssueEntries table."""
        conditions = ["1=1"]
        params = []
        
        if karigar_name:
            conditions.append("k.KarigarName LIKE ?")
            params.append(f"%{karigar_name}%")
        if item_type:
            conditions.append("t.ItemName LIKE ?")
            params.append(f"%{item_type}%")
        if date_from:
            dt = parse_date(date_from)
            if dt:
                conditions.append("i.IssueDate >= ?")
                params.append(dt)
        if date_to:
            dt = parse_date(date_to)
            if dt:
                conditions.append("i.IssueDate <= ?")
                params.append(dt)
        if month:
            conditions.append("MONTH(i.IssueDate) = ?")
            params.append(month)
        if year:
            conditions.append("YEAR(i.IssueDate) = ?")
            params.append(year)
        if weight_min is not None:
            conditions.append("i.Weight >= ?")
            params.append(weight_min)
        if weight_max is not None:
            conditions.append("i.Weight <= ?")
            params.append(weight_max)
        if remark:
            conditions.append("i.Remark LIKE ?")
            params.append(f"%{remark}%")
        
        where = " AND ".join(conditions)
        query = f"""
            SELECT i.IssueID AS RecordID, 'Issue' AS EntryType, 
                   i.IssueDate AS EntryDate, k.KarigarName, t.ItemName AS ItemType,
                   i.Remark, i.Weight, 0 AS GrossWeight, 0 AS LabourWeight,
                   0 AS ScrapWeight, i.AdvanceMoney, i.KarigarID, i.ItemTypeID
            FROM (IssueEntries i 
                INNER JOIN Karigars k ON i.KarigarID = k.KarigarID) 
                INNER JOIN ItemTypes t ON i.ItemTypeID = t.ItemTypeID
            WHERE {where}
            ORDER BY i.IssueDate DESC
        """
        
        rows = self._db.execute_query(query, tuple(params))
        return [self._format_result(row) for row in rows]
    
    def _search_receives(self, karigar_name, item_type, date_from, date_to,
                         month, year, weight_min, weight_max, remark) -> List[Dict]:
        """Search in ReceiveEntries table."""
        conditions = ["1=1"]
        params = []
        
        if karigar_name:
            conditions.append("k.KarigarName LIKE ?")
            params.append(f"%{karigar_name}%")
        if item_type:
            conditions.append("t.ItemName LIKE ?")
            params.append(f"%{item_type}%")
        if date_from:
            dt = parse_date(date_from)
            if dt:
                conditions.append("r.ReceiveDate >= ?")
                params.append(dt)
        if date_to:
            dt = parse_date(date_to)
            if dt:
                conditions.append("r.ReceiveDate <= ?")
                params.append(dt)
        if month:
            conditions.append("MONTH(r.ReceiveDate) = ?")
            params.append(month)
        if year:
            conditions.append("YEAR(r.ReceiveDate) = ?")
            params.append(year)
        if weight_min is not None:
            conditions.append("r.GrossWeight >= ?")
            params.append(weight_min)
        if weight_max is not None:
            conditions.append("r.GrossWeight <= ?")
            params.append(weight_max)
        if remark:
            conditions.append("r.Remark LIKE ?")
            params.append(f"%{remark}%")
        
        where = " AND ".join(conditions)
        query = f"""
            SELECT r.ReceiveID AS RecordID, 'Receive' AS EntryType,
                   r.ReceiveDate AS EntryDate, k.KarigarName, t.ItemName AS ItemType,
                   r.Remark, 0 AS Weight, r.GrossWeight, r.LabourWeight,
                   r.ScrapWeight, 0 AS AdvanceMoney, r.KarigarID, r.ItemTypeID
            FROM (ReceiveEntries r 
                INNER JOIN Karigars k ON r.KarigarID = k.KarigarID) 
                INNER JOIN ItemTypes t ON r.ItemTypeID = t.ItemTypeID
            WHERE {where}
            ORDER BY r.ReceiveDate DESC
        """
        
        rows = self._db.execute_query(query, tuple(params))
        return [self._format_result(row) for row in rows]
    
    def _format_result(self, row: dict) -> dict:
        """Format a search result for display."""
        return {
            "record_id": row.get("RecordID"),
            "entry_type": row.get("EntryType", ""),
            "entry_date": row.get("EntryDate"),
            "karigar_name": row.get("KarigarName", ""),
            "item_type": row.get("ItemType", ""),
            "remark": row.get("Remark", ""),
            "weight": float(row.get("Weight", 0) or 0),
            "gross_weight": float(row.get("GrossWeight", 0) or 0),
            "labour_weight": float(row.get("LabourWeight", 0) or 0),
            "scrap_weight": float(row.get("ScrapWeight", 0) or 0),
            "advance_money": float(row.get("AdvanceMoney", 0) or 0),
            "karigar_id": row.get("KarigarID"),
            "item_type_id": row.get("ItemTypeID"),
        }
