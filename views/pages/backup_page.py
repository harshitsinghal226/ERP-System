"""
Backup & Archive Page — Monthly backup, restore, and browse old databases.
"""

import customtkinter as ctk
import logging

from utils.theme import Fonts, get_theme
from utils.helpers import format_date
from views.components.data_table import DataTable
from views.components.toast import Toast
from views.components.confirmation_dialog import ConfirmationDialog

logger = logging.getLogger(__name__)


class BackupPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        theme = get_theme(ctk.get_appearance_mode().lower())
        super().__init__(parent, fg_color=theme.BG_PRIMARY)
        self._app = app
        self._theme = theme
        
        from services.backup_service import BackupService
        self._backup_svc = BackupService()
        
        self._build_ui()
        self._load_backups()
    
    def _build_ui(self):
        theme = self._theme
        
        # ── Action Card ──────────────────────────────────────────────
        action_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=12)
        action_frame.pack(fill="x", padx=20, pady=(16, 8))
        
        inner = ctk.CTkFrame(action_frame, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)
        
        # Title
        ctk.CTkLabel(
            inner, text="📦 Start New Month",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=16, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            inner, text="Create a backup of the current database before starting a new month.\nThe backup will be saved and you can browse it anytime.",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=11),
            text_color=theme.TEXT_MUTED, justify="left",
        ).pack(anchor="w", pady=(4, 12))
        
        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x")
        
        ctk.CTkButton(
            btn_row, text="🚀 Create Backup Now",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=13, weight="bold"),
            fg_color=theme.ACCENT_GOLD, text_color=theme.TEXT_ON_ACCENT,
            height=40, width=200, corner_radius=8,
            command=self._on_create_backup,
        ).pack(side="left")
        
        self._remark_entry = ctk.CTkEntry(
            btn_row, font=ctk.CTkFont(family=Fonts.FAMILY, size=11),
            height=40, width=300, placeholder_text="Backup remarks (optional)..."
        )
        self._remark_entry.pack(side="left", padx=12)
        
        # ── Backup History ───────────────────────────────────────────
        history_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=12)
        history_frame.pack(fill="both", expand=True, padx=20, pady=(8, 16))
        
        header = ctk.CTkFrame(history_frame, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 4))
        
        ctk.CTkLabel(
            header, text="Backup History",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
        ).pack(side="left")
        
        ctk.CTkButton(
            header, text="🔄 Refresh", command=self._load_backups,
            fg_color="transparent", border_width=1,
            height=30, width=80, corner_radius=6,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=10),
        ).pack(side="right")
        
        self._table = DataTable(
            history_frame,
            columns=[
                ("id", "ID", 50),
                ("month", "Month", 60),
                ("year", "Year", 60),
                ("date", "Backup Date", 140),
                ("path", "File Path", 350),
                ("remarks", "Remarks", 200),
            ],
            on_select=self._on_select,
        )
        self._table.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        
        # Action buttons for selected backup
        self._action_frame = ctk.CTkFrame(history_frame, fg_color="transparent")
        self._action_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        ctk.CTkButton(self._action_frame, text="📂 Open Location", command=self._on_open_location, fg_color=theme.ACCENT_BLUE, text_color="white", height=32, width=120, corner_radius=6).pack(side="left", padx=2)
        ctk.CTkButton(self._action_frame, text="🗑 Delete Backup", command=self._on_delete, fg_color="#dc2626", text_color="white", height=32, width=120, corner_radius=6).pack(side="left", padx=2)
    
    def _load_backups(self):
        try:
            backups = self._backup_svc.get_all_backups()
            data = []
            for b in backups:
                data.append([
                    b.backup_id, b.backup_month, b.backup_year,
                    format_date(b.backup_date) if b.backup_date else "",
                    b.backup_path, b.remarks or "",
                ])
            self._table.load_data(data)
        except Exception as e:
            logger.error(f"Failed to load backups: {e}")
    
    def _on_create_backup(self):
        if ConfirmationDialog.ask(
            self._app, "Create Backup",
            "This will create a backup of the current database.\nContinue?",
            confirm_text="Yes, Create Backup", danger=False
        ):
            try:
                backup = self._backup_svc.create_monthly_backup(
                    remarks=self._remark_entry.get().strip()
                )
                Toast.show(self._app, f"Backup created: {backup.backup_path}", "success")
                self._remark_entry.delete(0, "end")
                self._load_backups()
            except Exception as e:
                Toast.show(self._app, f"Backup failed: {e}", "error")
    
    def _on_select(self, values):
        self._selected_backup = values if values else None
    
    def _on_open_location(self):
        if not hasattr(self, '_selected_backup') or not self._selected_backup:
            Toast.show(self._app, "Select a backup first", "warning")
            return
        
        import os
        path = str(self._selected_backup[4])
        if os.path.exists(path):
            from services.print_service import PrintService
            PrintService.share_file(path)
        else:
            Toast.show(self._app, "Backup file not found", "error")
    
    def _on_delete(self):
        if not hasattr(self, '_selected_backup') or not self._selected_backup:
            Toast.show(self._app, "Select a backup first", "warning")
            return
        
        if ConfirmationDialog.ask(self._app, "Delete Backup", "This will permanently delete the backup file.\nAre you sure?"):
            try:
                backup_id = int(self._selected_backup[0])
                self._backup_svc.delete_backup(backup_id)
                Toast.show(self._app, "Backup deleted", "success")
                self._load_backups()
            except Exception as e:
                Toast.show(self._app, f"Error: {e}", "error")
