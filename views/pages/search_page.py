"""
Search Page — Multi-criteria search across Issue and Receive entries.
"""

import customtkinter as ctk
import logging

from utils.theme import Fonts, get_theme
from utils.helpers import format_date, format_weight, format_currency, safe_float
from utils.constants import MONTHS
from views.components.data_table import DataTable
from views.components.toast import Toast

logger = logging.getLogger(__name__)


class SearchPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        theme = get_theme(ctk.get_appearance_mode().lower())
        super().__init__(parent, fg_color=theme.BG_PRIMARY)
        self._app = app
        self._theme = theme
        
        from services.search_service import SearchService
        self._search_svc = SearchService()
        
        self._build_ui()
    
    def _build_ui(self):
        theme = self._theme
        
        # ── Search Filters ───────────────────────────────────────────
        filter_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=12)
        filter_frame.pack(fill="x", padx=20, pady=(16, 8))
        
        inner = ctk.CTkFrame(filter_frame, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)
        
        # Row 1
        row1 = ctk.CTkFrame(inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 8))
        for i in range(5):
            row1.grid_columnconfigure(i, weight=1, uniform="s")
        
        ctk.CTkLabel(row1, text="Karigar", font=ctk.CTkFont(family=Fonts.FAMILY, size=10, weight="bold"), text_color=theme.TEXT_MUTED).grid(row=0, column=0, sticky="w")
        self._karigar_entry = ctk.CTkEntry(row1, height=34, placeholder_text="Name...")
        self._karigar_entry.grid(row=1, column=0, padx=(0, 4), sticky="ew")
        
        ctk.CTkLabel(row1, text="Item Type", font=ctk.CTkFont(family=Fonts.FAMILY, size=10, weight="bold"), text_color=theme.TEXT_MUTED).grid(row=0, column=1, sticky="w")
        self._item_entry = ctk.CTkEntry(row1, height=34, placeholder_text="Type...")
        self._item_entry.grid(row=1, column=1, padx=4, sticky="ew")
        
        ctk.CTkLabel(row1, text="Date From", font=ctk.CTkFont(family=Fonts.FAMILY, size=10, weight="bold"), text_color=theme.TEXT_MUTED).grid(row=0, column=2, sticky="w")
        self._date_from = ctk.CTkEntry(row1, height=34, placeholder_text="DD-MM-YYYY")
        self._date_from.grid(row=1, column=2, padx=4, sticky="ew")
        
        ctk.CTkLabel(row1, text="Date To", font=ctk.CTkFont(family=Fonts.FAMILY, size=10, weight="bold"), text_color=theme.TEXT_MUTED).grid(row=0, column=3, sticky="w")
        self._date_to = ctk.CTkEntry(row1, height=34, placeholder_text="DD-MM-YYYY")
        self._date_to.grid(row=1, column=3, padx=4, sticky="ew")
        
        ctk.CTkLabel(row1, text="Entry Type", font=ctk.CTkFont(family=Fonts.FAMILY, size=10, weight="bold"), text_color=theme.TEXT_MUTED).grid(row=0, column=4, sticky="w")
        self._type_combo = ctk.CTkComboBox(row1, height=34, values=["All", "Issue", "Receive"], state="readonly")
        self._type_combo.grid(row=1, column=4, padx=(4, 0), sticky="ew")
        self._type_combo.set("All")
        
        # Row 2
        row2 = ctk.CTkFrame(inner, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 8))
        
        ctk.CTkLabel(row2, text="Remark", font=ctk.CTkFont(family=Fonts.FAMILY, size=10, weight="bold"), text_color=theme.TEXT_MUTED).pack(side="left")
        self._remark_entry = ctk.CTkEntry(row2, height=34, width=200, placeholder_text="Remark...")
        self._remark_entry.pack(side="left", padx=(4, 16))
        
        ctk.CTkButton(
            row2, text="🔍 Search", command=self._on_search,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=12, weight="bold"),
            fg_color=theme.ACCENT_GOLD, text_color=theme.TEXT_ON_ACCENT,
            width=120, height=34, corner_radius=8,
        ).pack(side="left", padx=4)
        
        ctk.CTkButton(
            row2, text="🧹 Clear", command=self._on_clear,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=12),
            fg_color="transparent", border_width=1,
            width=80, height=34, corner_radius=8,
        ).pack(side="left", padx=4)
        
        self._result_label = ctk.CTkLabel(
            row2, text="", font=ctk.CTkFont(family=Fonts.FAMILY, size=11),
            text_color=theme.TEXT_MUTED,
        )
        self._result_label.pack(side="right")
        
        # ── Results Table ────────────────────────────────────────────
        table_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=12)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(8, 16))
        
        self._table = DataTable(
            table_frame,
            columns=[
                ("type", "Type", 70), ("date", "Date", 100),
                ("karigar", "Karigar", 140), ("item", "Item", 120),
                ("weight", "Weight (g)", 100), ("gross", "Gross (g)", 90),
                ("labour", "Labour (g)", 90), ("advance", "Advance", 100),
                ("remark", "Remark", 200),
            ],
            on_double_click=self._on_row_click,
        )
        self._table.pack(fill="both", expand=True, padx=12, pady=12)
    
    def _on_search(self):
        type_map = {"All": "", "Issue": "I", "Receive": "R"}
        entry_type = type_map.get(self._type_combo.get(), "")
        
        try:
            results = self._search_svc.search(
                karigar_name=self._karigar_entry.get().strip(),
                item_type=self._item_entry.get().strip(),
                date_from=self._date_from.get().strip(),
                date_to=self._date_to.get().strip(),
                entry_type=entry_type,
                remark=self._remark_entry.get().strip(),
            )
            
            data = []
            for r in results:
                data.append([
                    r["entry_type"], format_date(r["entry_date"]),
                    r["karigar_name"], r["item_type"],
                    format_weight(r["weight"]) if r["weight"] else "",
                    format_weight(r["gross_weight"]) if r["gross_weight"] else "",
                    format_weight(r["labour_weight"]) if r["labour_weight"] else "",
                    format_currency(r["advance_money"]) if r["advance_money"] else "",
                    r["remark"] or "",
                ])
            
            self._table.load_data(data)
            self._result_label.configure(text=f"{len(results)} results found")
        except Exception as e:
            Toast.show(self._app, f"Search error: {e}", "error")
    
    def _on_clear(self):
        for entry in [self._karigar_entry, self._item_entry, self._date_from,
                       self._date_to, self._remark_entry]:
            entry.delete(0, "end")
        self._type_combo.set("All")
        self._table.clear()
        self._result_label.configure(text="")
    
    def _on_row_click(self, values):
        """Navigate to the appropriate edit page based on entry type."""
        if values and len(values) > 0:
            entry_type = str(values[0])
            if entry_type == "Issue":
                self._app.navigate_to("issue")
            elif entry_type == "Receive":
                self._app.navigate_to("receive")
