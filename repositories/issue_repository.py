"""
Issue Entry repository — CRUD operations for IssueEntries table.
"""

import logging
from datetime import datetime
from typing import List, Optional

from database.connection import DatabaseConnection
from models.issue_entry import IssueEntry
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class IssueRepository(BaseRepository):
    
    def __init__(self, db: DatabaseConnection = None):
        super().__init__(db)
    
    @property
    def table_name(self) -> str:
        return "IssueEntries"
    
    @property
    def primary_key(self) -> str:
        return "IssueID"
    
    def _map_to_model(self, row: dict) -> IssueEntry:
        return IssueEntry.from_dict(row)
    
    def _get_searchable_columns(self) -> List[str]:
        return ["Remark"]
    
    def create(self, entry: IssueEntry) -> int:
        query = (
            "INSERT INTO IssueEntries "
            "(IssueDate, KarigarID, ItemTypeID, Remark, Weight, AdvanceMoney, CreatedAt, UpdatedAt) "
            "VALUES (?, ?, ?, ?, ?, ?, NOW(), NOW())"
        )
        params = (
            entry.issue_date, entry.karigar_id, entry.item_type_id,
            entry.remark, entry.weight, entry.advance_money,
        )
        new_id = self._db.execute_non_query(query, params)
        logger.info(f"Created IssueEntry ID {new_id}: {entry.weight}g to Karigar {entry.karigar_id}")
        return new_id
    
    def update(self, entry: IssueEntry) -> bool:
        query = (
            "UPDATE IssueEntries SET "
            "IssueDate = ?, KarigarID = ?, ItemTypeID = ?, Remark = ?, "
            "Weight = ?, AdvanceMoney = ?, UpdatedAt = NOW() "
            "WHERE IssueID = ?"
        )
        params = (
            entry.issue_date, entry.karigar_id, entry.item_type_id,
            entry.remark, entry.weight, entry.advance_money,
            entry.issue_id,
        )
        return self._db.execute_non_query(query, params) > 0
    
    def get_all_with_details(self) -> List[IssueEntry]:
        """Get all issue entries with Karigar and ItemType names joined."""
        query = (
            "SELECT i.*, k.KarigarName, t.ItemName "
            "FROM (IssueEntries i "
            "INNER JOIN Karigars k ON i.KarigarID = k.KarigarID) "
            "INNER JOIN ItemTypes t ON i.ItemTypeID = t.ItemTypeID "
            "ORDER BY i.IssueDate DESC, i.IssueID DESC"
        )
        rows = self._db.execute_query(query)
        return [self._map_to_model(row) for row in rows]
    
    def get_by_karigar(self, karigar_id: int) -> List[IssueEntry]:
        """Get all issues for a specific Karigar."""
        query = (
            "SELECT i.*, k.KarigarName, t.ItemName "
            "FROM (IssueEntries i "
            "INNER JOIN Karigars k ON i.KarigarID = k.KarigarID) "
            "INNER JOIN ItemTypes t ON i.ItemTypeID = t.ItemTypeID "
            "WHERE i.KarigarID = ? "
            "ORDER BY i.IssueDate ASC"
        )
        rows = self._db.execute_query(query, (karigar_id,))
        return [self._map_to_model(row) for row in rows]
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[IssueEntry]:
        """Get issues within a date range."""
        query = (
            "SELECT i.*, k.KarigarName, t.ItemName "
            "FROM (IssueEntries i "
            "INNER JOIN Karigars k ON i.KarigarID = k.KarigarID) "
            "INNER JOIN ItemTypes t ON i.ItemTypeID = t.ItemTypeID "
            "WHERE i.IssueDate >= ? AND i.IssueDate <= ? "
            "ORDER BY i.IssueDate ASC"
        )
        rows = self._db.execute_query(query, (start_date, end_date))
        return [self._map_to_model(row) for row in rows]
    
    def get_by_month_year(self, month: int, year: int) -> List[IssueEntry]:
        """Get issues for a specific month and year."""
        query = (
            "SELECT i.*, k.KarigarName, t.ItemName "
            "FROM (IssueEntries i "
            "INNER JOIN Karigars k ON i.KarigarID = k.KarigarID) "
            "INNER JOIN ItemTypes t ON i.ItemTypeID = t.ItemTypeID "
            "WHERE MONTH(i.IssueDate) = ? AND YEAR(i.IssueDate) = ? "
            "ORDER BY i.IssueDate ASC"
        )
        rows = self._db.execute_query(query, (month, year))
        return [self._map_to_model(row) for row in rows]
    
    def get_today_total(self) -> dict:
        """Get today's issue totals."""
        query = (
            "SELECT COUNT(*) AS cnt, "
            "IIF(SUM(Weight) IS NULL, 0, SUM(Weight)) AS total_weight, "
            "IIF(SUM(AdvanceMoney) IS NULL, 0, SUM(AdvanceMoney)) AS total_advance "
            "FROM IssueEntries "
            "WHERE IssueDate >= ? AND IssueDate < ?"
        )
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today.replace(hour=23, minute=59, second=59)
        result = self._db.execute_query(query, (today, tomorrow))
        if result:
            return result[0]
        return {"cnt": 0, "total_weight": 0, "total_advance": 0}
    
    def get_karigar_total_issued(self, karigar_id: int) -> float:
        """Get total weight issued to a Karigar."""
        query = (
            "SELECT IIF(SUM(Weight) IS NULL, 0, SUM(Weight)) AS total "
            "FROM IssueEntries WHERE KarigarID = ?"
        )
        result = self._db.execute_query(query, (karigar_id,))
        return float(result[0]["total"]) if result else 0.0
    
    def get_karigar_total_advance(self, karigar_id: int) -> float:
        """Get total advance money given to a Karigar."""
        query = (
            "SELECT IIF(SUM(AdvanceMoney) IS NULL, 0, SUM(AdvanceMoney)) AS total "
            "FROM IssueEntries WHERE KarigarID = ?"
        )
        result = self._db.execute_query(query, (karigar_id,))
        return float(result[0]["total"]) if result else 0.0
    
    def get_grand_total_issued(self) -> float:
        """Get total weight issued across all Karigars."""
        query = "SELECT IIF(SUM(Weight) IS NULL, 0, SUM(Weight)) AS total FROM IssueEntries"
        result = self._db.execute_query(query)
        return float(result[0]["total"]) if result else 0.0
    
    def get_grand_total_advance(self) -> float:
        """Get total advance money across all Karigars."""
        query = "SELECT IIF(SUM(AdvanceMoney) IS NULL, 0, SUM(AdvanceMoney)) AS total FROM IssueEntries"
        result = self._db.execute_query(query)
        return float(result[0]["total"]) if result else 0.0
