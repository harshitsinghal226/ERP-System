"""
Receive Entry Page — Form for recording silver received from Karigars.
Features auto-calculation of Scrap and Net weight.
"""

import customtkinter as ctk
import logging
from datetime import datetime

from utils.theme import Fonts, get_theme
from utils.helpers import today_str, format_date, format_weight, safe_float
from utils.validators import validate_receive_entry
from views.components.data_table import DataTable
from views.components.toast import Toast
from views.components.confirmation_dialog import ConfirmationDialog
from views.components.searchable_combo import SearchableComboBox

logger = logging.getLogger(__name__)


class ReceivePage(ctk.CTkFrame):
    """Receive Entry form with auto-calc and CRUD."""
    
    def __init__(self, parent, app):
        theme = get_theme(ctk.get_appearance_mode().lower())
        super().__init__(parent, fg_color=theme.BG_PRIMARY)
        self._app = app
        self._theme = theme
        self._selected_id = None
        
        from services.receive_service import ReceiveService
        from services.karigar_service import KarigarService
        from repositories.item_type_repository import ItemTypeRepository
        self._receive_svc = ReceiveService()
        self._karigar_svc = KarigarService()
        self._item_type_repo = ItemTypeRepository()
        
        self._build_ui()
        self._load_dropdowns()
        self._load_table()
    
    def _build_ui(self):
        theme = self._theme
        
        # Form
        form_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=12)
        form_frame.pack(fill="x", padx=20, pady=(16, 8))
        
        form_inner = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_inner.pack(fill="x", padx=20, pady=16)
        
        # Row 1: Date, Karigar, Item Type
        row1 = ctk.CTkFrame(form_inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        for i in range(3):
            row1.grid_columnconfigure(i, weight=1, uniform="f")
        
        # Date
        self._build_label(row1, "Date *", 0, 0)
        self._date_entry = ctk.CTkEntry(row1, font=ctk.CTkFont(family=Fonts.FAMILY, size=14), height=36)
        self._date_entry.grid(row=1, column=0, padx=(0, 8), sticky="ew")
        self._date_entry.insert(0, datetime.now().strftime("%d-%m-%Y"))
        
        # Karigar
        self._build_label(row1, "Karigar *", 0, 1)
        self._karigar_combo = SearchableComboBox(row1, font=ctk.CTkFont(family=Fonts.FAMILY, size=14), height=36)
        self._karigar_combo.grid(row=1, column=1, padx=4, sticky="ew")
        self._karigar_combo.set("")
        
        # Item Type
        self._build_label(row1, "Item Type *", 0, 2)
        self._item_combo = SearchableComboBox(row1, font=ctk.CTkFont(family=Fonts.FAMILY, size=14), height=36)
        self._item_combo.grid(row=1, column=2, padx=(8, 0), sticky="ew")
        self._item_combo.set("")
        
        # Row 2: Gross, Labour, Scrap, Net Weight
        row2 = ctk.CTkFrame(form_inner, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))
        for i in range(4):
            row2.grid_columnconfigure(i, weight=1, uniform="f")
        
        # Gross Weight
        self._build_label(row2, "Gross Weight (g) *", 0, 0)
        self._gross_entry = ctk.CTkEntry(row2, font=ctk.CTkFont(family=Fonts.FAMILY, size=14), height=36, placeholder_text="0.000")
        self._gross_entry.grid(row=1, column=0, padx=(0, 8), sticky="ew")
        self._gross_entry.bind("<KeyRelease>", self._auto_calculate)
        
        # Labour Weight
        self._build_label(row2, "Labour Weight (g) *", 0, 1)
        self._labour_entry = ctk.CTkEntry(row2, font=ctk.CTkFont(family=Fonts.FAMILY, size=14), height=36, placeholder_text="0.000")
        self._labour_entry.grid(row=1, column=1, padx=4, sticky="ew")
        self._labour_entry.bind("<KeyRelease>", self._auto_calculate)
        
        self._build_label(row2, "Scrap Weight (auto)", 0, 2)
        self._scrap_label = ctk.CTkLabel(
            row2, text="0.000 g",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=14, weight="bold"),
            text_color="#fbbf24", height=36, anchor="w",
        )
        self._scrap_label.grid(row=1, column=2, padx=4, sticky="ew")
        
        self._build_label(row2, "Net Weight (auto)", 0, 3)
        self._net_label = ctk.CTkLabel(
            row2, text="0.000 g",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=14, weight="bold"),
            text_color="#34d399", height=36, anchor="w",
        )
        self._net_label.grid(row=1, column=3, padx=(8, 0), sticky="ew")
        
        # Row 3: Remark
        row3 = ctk.CTkFrame(form_inner, fg_color="transparent")
        row3.pack(fill="x", pady=(0, 12))
        
        # Remark
        self._build_label_simple(row3, "Remark")
        self._remark_entry = ctk.CTkEntry(row3, font=ctk.CTkFont(family=Fonts.FAMILY, size=14), height=36, placeholder_text="Optional")
        self._remark_entry.pack(fill="x")
        
        # ── Setup Enter Navigation ───────────────────────────────────
        self._setup_enter_navigation()
        
        # Buttons
        btn_frame = ctk.CTkFrame(form_inner, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        buttons = [
            ("📄 New (Ctrl+N)", self._on_new, "transparent", theme.TEXT_PRIMARY),
            ("💾 Save (Ctrl+S)", self._on_save, theme.ACCENT_GOLD, theme.TEXT_ON_ACCENT),
            ("✏️ Update", self._on_update, theme.ACCENT_BLUE, "white"),
            ("🗑 Delete (Del)", self._on_delete, "#dc2626", "white"),
            ("🧹 Clear", self._on_clear, "transparent", theme.TEXT_SECONDARY),
        ]
        
        for text, cmd, fg, tc in buttons:
            ctk.CTkButton(
                btn_frame, text=text, command=cmd,
                font=ctk.CTkFont(family=Fonts.FAMILY, size=13, weight="bold"),
                fg_color=fg, text_color=tc,
                border_width=1 if fg == "transparent" else 0,
                height=36, corner_radius=8,
            ).pack(side="left", padx=4)
        
        # Table
        table_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=12)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(8, 16))
        
        ctk.CTkLabel(
            table_frame, text="Recent Receive Entries",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=13, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(12, 4))
        
        self._table = DataTable(
            table_frame,
            columns=[
                ("id", "ID", 50),
                ("date", "Date", 100),
                ("karigar", "Karigar", 140),
                ("item", "Item Type", 120),
                ("gross", "Gross (g)", 90),
                ("labour", "Labour (g)", 90),
                ("scrap", "Scrap (g)", 90),
                ("net", "Net (g)", 90),
                ("remark", "Remark", 160),
            ],
            on_select=self._on_table_select,
            on_double_click=self._on_table_select,
        )
        self._table.pack(fill="both", expand=True, padx=12, pady=(0, 12))
    
    def _build_label(self, parent, text, row, col):
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=12, weight="bold"),
            text_color=self._theme.TEXT_MUTED,
        ).grid(row=row, column=col, sticky="w", padx=4 if col > 0 else 0)
    
    def _build_label_simple(self, parent, text):
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=12, weight="bold"),
            text_color=self._theme.TEXT_MUTED,
        ).pack(anchor="w")
        
    def _setup_enter_navigation(self):
        """Bind Enter key to navigate to the next field."""
        fields = [
            self._date_entry,
            self._karigar_combo,
            self._item_combo,
            self._gross_entry,
            self._labour_entry,
            self._remark_entry
        ]
        
        for i, field in enumerate(fields):
            widget = field._entry if hasattr(field, "_entry") else field
            if i < len(fields) - 1:
                next_field = fields[i + 1]
                next_widget = next_field._entry if hasattr(next_field, "_entry") else next_field
                widget.bind("<Return>", lambda e, w=next_widget: w.focus_set())
            else:
                widget.bind("<Return>", self._on_enter_submit)
                
    def _on_enter_submit(self, event=None):
        """Submit the form via Enter key."""
        if self._selected_id:
            self._on_update()
        else:
            self._on_save()
    
    def _auto_calculate(self, event=None):
        """Real-time auto-calculation of Scrap and Net weight."""
        gross = safe_float(self._gross_entry.get())
        labour = safe_float(self._labour_entry.get())
        
        scrap = max(0, gross - labour)
        net = max(0, gross - scrap)  # = labour
        
        self._scrap_label.configure(text=f"{format_weight(scrap)} g")
        self._net_label.configure(text=f"{format_weight(net)} g")
    
    def _load_dropdowns(self):
        try:
            karigars = self._karigar_svc.get_active()
            self._karigar_map = {k.karigar_name.lower(): k.karigar_id for k in karigars}
            self._karigar_combo.set_all_values([k.karigar_name for k in karigars])
            
            items = self._item_type_repo.get_active()
            self._item_map = {it.item_name.lower(): it.item_type_id for it in items}
            self._item_combo.set_all_values([it.item_name for it in items])
        except Exception as e:
            logger.error(f"Failed to load dropdowns: {e}")
    
    def _load_table(self):
        try:
            entries = self._receive_svc.get_all_with_details()
            data = []
            for e in entries:
                data.append([
                    e.receive_id, format_date(e.receive_date), e.karigar_name,
                    e.item_type_name, format_weight(e.gross_weight),
                    format_weight(e.labour_weight), format_weight(e.scrap_weight),
                    format_weight(e.net_weight), e.remark or "",
                ])
            self._table.load_data(data)
        except Exception as e:
            logger.error(f"Failed to load table: {e}")
    
    def _on_save(self, event=None):
        karigar_name = self._karigar_combo.get().strip()
        item_name = self._item_combo.get().strip()
        
        errors = validate_receive_entry(
            self._date_entry.get(), karigar_name,
            item_name, self._gross_entry.get() or "0",
            self._labour_entry.get() or "0",
        )
        if errors:
            Toast.show(self._app, errors[0].message, "error")
            return
            
        karigar_id = self._karigar_map.get(karigar_name.lower())
        item_id = self._item_map.get(item_name.lower())
        
        if not karigar_id:
            Toast.show(self._app, "Invalid Karigar selected", "error")
            return
        if not item_id:
            Toast.show(self._app, "Invalid Item Type selected", "error")
            return
        
        try:
            self._receive_svc.create(
                date_str=self._date_entry.get(),
                karigar_id=karigar_id,
                item_type_id=item_id,
                remark=self._remark_entry.get(),
                gross_weight=safe_float(self._gross_entry.get()),
                labour_weight=safe_float(self._labour_entry.get()),
            )
            Toast.show(self._app, "Receive entry saved!", "success")
            self._on_clear()
            self._load_table()
            
            # Restore focus to first field for continuous entry
            self._date_entry.focus_set()
        except Exception as e:
            Toast.show(self._app, f"Error: {e}", "error")
    
    def _on_update(self, event=None):
        if not self._selected_id:
            Toast.show(self._app, "Select a record to update", "warning")
            return
        karigar_name = self._karigar_combo.get().strip()
        item_name = self._item_combo.get().strip()
        
        karigar_id = self._karigar_map.get(karigar_name.lower())
        item_id = self._item_map.get(item_name.lower())
        
        if not karigar_id:
            Toast.show(self._app, "Invalid Karigar selected", "error")
            return
        if not item_id:
            Toast.show(self._app, "Invalid Item Type selected", "error")
            return
            
        try:
            self._receive_svc.update(
                receive_id=self._selected_id,
                date_str=self._date_entry.get(),
                karigar_id=karigar_id,
                item_type_id=item_id,
                remark=self._remark_entry.get(),
                gross_weight=safe_float(self._gross_entry.get()),
                labour_weight=safe_float(self._labour_entry.get()),
            )
            Toast.show(self._app, "Receive entry updated!", "success")
            self._on_clear()
            self._load_table()
        except Exception as e:
            Toast.show(self._app, f"Error: {e}", "error")
    
    def _on_delete(self, event=None):
        if not self._selected_id:
            Toast.show(self._app, "Select a record to delete", "warning")
            return
        if ConfirmationDialog.ask(self._app, "Delete Receive Entry",
                                  "Are you sure? This cannot be undone."):
            try:
                self._receive_svc.delete(self._selected_id)
                Toast.show(self._app, "Receive entry deleted", "success")
                self._on_clear()
                self._load_table()
            except Exception as e:
                Toast.show(self._app, f"Error: {e}", "error")
    
    def _on_new(self, event=None):
        self._on_clear()
        self._date_entry.delete(0, "end")
        self._date_entry.insert(0, today_str())
    
    def _on_clear(self, event=None):
        self._selected_id = None
        self._date_entry.delete(0, "end")
        self._date_entry.insert(0, today_str())
        self._karigar_combo.set("")
        self._item_combo.set("")
        self._gross_entry.delete(0, "end")
        self._labour_entry.delete(0, "end")
        self._remark_entry.delete(0, "end")
        self._scrap_label.configure(text="0.000 g")
        self._net_label.configure(text="0.000 g")
    
    def _on_table_select(self, values):
        if not values:
            return
        try:
            self._selected_id = int(values[0])
            entry = self._receive_svc.get_by_id(self._selected_id)
            if not entry:
                return
            
            self._date_entry.delete(0, "end")
            self._date_entry.insert(0, format_date(entry.receive_date))
            
            for name, kid in self._karigar_map.items():
                if kid == entry.karigar_id:
                    self._karigar_combo.set(name)
                    break
            for name, itid in self._item_map.items():
                if itid == entry.item_type_id:
                    self._item_combo.set(name)
                    break
            
            self._gross_entry.delete(0, "end")
            self._gross_entry.insert(0, str(entry.gross_weight))
            self._labour_entry.delete(0, "end")
            self._labour_entry.insert(0, str(entry.labour_weight))
            self._remark_entry.delete(0, "end")
            self._remark_entry.insert(0, entry.remark or "")
            self._auto_calculate()
        except Exception as e:
            logger.error(f"Error loading entry: {e}")
