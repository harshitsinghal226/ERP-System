"""
Receive Entry repository — CRUD operations for ReceiveEntries table.
"""

import logging
from datetime import datetime
from typing import List

from database.connection import DatabaseConnection
from models.receive_entry import ReceiveEntry
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ReceiveRepository(BaseRepository):
    
    def __init__(self, db: DatabaseConnection = None):
        super().__init__(db)
    
    @property
    def table_name(self) -> str:
        return "ReceiveEntries"
    
    @property
    def primary_key(self) -> str:
        return "ReceiveID"
    
    def _map_to_model(self, row: dict) -> ReceiveEntry:
        return ReceiveEntry.from_dict(row)
    
    def _get_searchable_columns(self) -> List[str]:
        return ["Remark"]
    
    def create(self, entry: ReceiveEntry) -> int:
        query = (
            "INSERT INTO ReceiveEntries "
            "(ReceiveDate, KarigarID, ItemTypeID, Remark, "
            "GrossWeight, LabourWeight, ScrapWeight, NetWeight, CreatedAt, UpdatedAt) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, NOW(), NOW())"
        )
        params = (
            entry.receive_date, entry.karigar_id, entry.item_type_id,
            entry.remark, entry.gross_weight, entry.labour_weight,
            entry.scrap_weight, entry.net_weight,
        )
        new_id = self._db.execute_non_query(query, params)
        logger.info(f"Created ReceiveEntry ID {new_id}: {entry.gross_weight}g from Karigar {entry.karigar_id}")
        return new_id
    
    def update(self, entry: ReceiveEntry) -> bool:
        query = (
            "UPDATE ReceiveEntries SET "
            "ReceiveDate = ?, KarigarID = ?, ItemTypeID = ?, Remark = ?, "
            "GrossWeight = ?, LabourWeight = ?, ScrapWeight = ?, NetWeight = ?, "
            "UpdatedAt = NOW() "
            "WHERE ReceiveID = ?"
        )
        params = (
            entry.receive_date, entry.karigar_id, entry.item_type_id,
            entry.remark, entry.gross_weight, entry.labour_weight,
            entry.scrap_weight, entry.net_weight,
            entry.receive_id,
        )
        return self._db.execute_non_query(query, params) > 0
    
    def get_all_with_details(self) -> List[ReceiveEntry]:
        query = (
            "SELECT r.*, k.KarigarName, t.ItemName "
            "FROM (ReceiveEntries r "
            "INNER JOIN Karigars k ON r.KarigarID = k.KarigarID) "
            "INNER JOIN ItemTypes t ON r.ItemTypeID = t.ItemTypeID "
            "ORDER BY r.ReceiveDate DESC, r.ReceiveID DESC"
        )
        rows = self._db.execute_query(query)
        return [self._map_to_model(row) for row in rows]
    
    def get_by_karigar(self, karigar_id: int) -> List[ReceiveEntry]:
        query = (
            "SELECT r.*, k.KarigarName, t.ItemName "
            "FROM (ReceiveEntries r "
            "INNER JOIN Karigars k ON r.KarigarID = k.KarigarID) "
            "INNER JOIN ItemTypes t ON r.ItemTypeID = t.ItemTypeID "
            "WHERE r.KarigarID = ? "
            "ORDER BY r.ReceiveDate ASC"
        )
        rows = self._db.execute_query(query, (karigar_id,))
        return [self._map_to_model(row) for row in rows]
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[ReceiveEntry]:
        query = (
            "SELECT r.*, k.KarigarName, t.ItemName "
            "FROM (ReceiveEntries r "
            "INNER JOIN Karigars k ON r.KarigarID = k.KarigarID) "
            "INNER JOIN ItemTypes t ON r.ItemTypeID = t.ItemTypeID "
            "WHERE r.ReceiveDate >= ? AND r.ReceiveDate <= ? "
            "ORDER BY r.ReceiveDate ASC"
        )
        rows = self._db.execute_query(query, (start_date, end_date))
        return [self._map_to_model(row) for row in rows]
    
    def get_by_month_year(self, month: int, year: int) -> List[ReceiveEntry]:
        query = (
            "SELECT r.*, k.KarigarName, t.ItemName "
            "FROM (ReceiveEntries r "
            "INNER JOIN Karigars k ON r.KarigarID = k.KarigarID) "
            "INNER JOIN ItemTypes t ON r.ItemTypeID = t.ItemTypeID "
            "WHERE MONTH(r.ReceiveDate) = ? AND YEAR(r.ReceiveDate) = ? "
            "ORDER BY r.ReceiveDate ASC"
        )
        rows = self._db.execute_query(query, (month, year))
        return [self._map_to_model(row) for row in rows]
    
    def get_today_total(self) -> dict:
        query = (
            "SELECT COUNT(*) AS cnt, "
            "IIF(SUM(GrossWeight) IS NULL, 0, SUM(GrossWeight)) AS total_gross, "
            "IIF(SUM(LabourWeight) IS NULL, 0, SUM(LabourWeight)) AS total_labour, "
            "IIF(SUM(ScrapWeight) IS NULL, 0, SUM(ScrapWeight)) AS total_scrap "
            "FROM ReceiveEntries "
            "WHERE ReceiveDate >= ? AND ReceiveDate < ?"
        )
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today.replace(hour=23, minute=59, second=59)
        result = self._db.execute_query(query, (today, tomorrow))
        if result:
            return result[0]
        return {"cnt": 0, "total_gross": 0, "total_labour": 0, "total_scrap": 0}
    
    def get_karigar_total_received(self, karigar_id: int) -> float:
        query = (
            "SELECT IIF(SUM(GrossWeight) IS NULL, 0, SUM(GrossWeight)) AS total "
            "FROM ReceiveEntries WHERE KarigarID = ?"
        )
        result = self._db.execute_query(query, (karigar_id,))
        return float(result[0]["total"]) if result else 0.0
    
    def get_karigar_total_labour(self, karigar_id: int) -> float:
        query = (
            "SELECT IIF(SUM(LabourWeight) IS NULL, 0, SUM(LabourWeight)) AS total "
            "FROM ReceiveEntries WHERE KarigarID = ?"
        )
        result = self._db.execute_query(query, (karigar_id,))
        return float(result[0]["total"]) if result else 0.0
    
    def get_grand_total_received(self) -> float:
        query = "SELECT IIF(SUM(GrossWeight) IS NULL, 0, SUM(GrossWeight)) AS total FROM ReceiveEntries"
        result = self._db.execute_query(query)
        return float(result[0]["total"]) if result else 0.0
    
    def get_grand_total_labour(self) -> float:
        query = "SELECT IIF(SUM(LabourWeight) IS NULL, 0, SUM(LabourWeight)) AS total FROM ReceiveEntries"
        result = self._db.execute_query(query)
        return float(result[0]["total"]) if result else 0.0
    
    def get_grand_total_scrap(self) -> float:
        query = "SELECT IIF(SUM(ScrapWeight) IS NULL, 0, SUM(ScrapWeight)) AS total FROM ReceiveEntries"
        result = self._db.execute_query(query)
        return float(result[0]["total"]) if result else 0.0
