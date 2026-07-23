"""
Karigar Management Page — Full CRUD for Karigars with status toggle.
"""

import customtkinter as ctk
import logging

from utils.theme import Fonts, get_theme
from utils.helpers import format_weight, format_currency, get_balance_status
from utils.validators import validate_karigar
from views.components.data_table import DataTable
from views.components.toast import Toast
from views.components.confirmation_dialog import ConfirmationDialog

logger = logging.getLogger(__name__)


class KarigarPage(ctk.CTkFrame):
    """Karigar management with CRUD, search, and balance display."""
    
    def __init__(self, parent, app):
        theme = get_theme(ctk.get_appearance_mode().lower())
        super().__init__(parent, fg_color=theme.BG_PRIMARY)
        self._app = app
        self._theme = theme
        self._selected_id = None
        
        from services.karigar_service import KarigarService
        self._karigar_svc = KarigarService()
        
        self._build_ui()
        self._load_table()
    
    def _build_ui(self):
        theme = self._theme
        
        # ── Form Card ────────────────────────────────────────────────
        form_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=12)
        form_frame.pack(fill="x", padx=20, pady=(16, 8))
        
        form_inner = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_inner.pack(fill="x", padx=20, pady=16)
        
        # Row 1: Name, Phone, City
        row1 = ctk.CTkFrame(form_inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        for i in range(3):
            row1.grid_columnconfigure(i, weight=1, uniform="f")
        
        self._lbl(row1, "Karigar Name *", 0, 0)
        self._name_entry = ctk.CTkEntry(row1, font=ctk.CTkFont(family=Fonts.FAMILY, size=14), height=36)
        self._name_entry.grid(row=1, column=0, padx=(0, 8), sticky="ew")
        
        self._lbl(row1, "Phone Number", 0, 1)
        self._phone_entry = ctk.CTkEntry(row1, font=ctk.CTkFont(family=Fonts.FAMILY, size=14), height=36)
        self._phone_entry.grid(row=1, column=1, padx=4, sticky="ew")
        
        self._lbl(row1, "City", 0, 2)
        self._city_entry = ctk.CTkEntry(row1, font=ctk.CTkFont(family=Fonts.FAMILY, size=14), height=36)
        self._city_entry.grid(row=1, column=2, padx=(8, 0), sticky="ew")
        
        # Row 2: Address, Opening Balance, Remark
        row2 = ctk.CTkFrame(form_inner, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 12))
        for i in range(3):
            row2.grid_columnconfigure(i, weight=1, uniform="f")
        
        self._lbl(row2, "Address", 0, 0)
        self._address_entry = ctk.CTkEntry(row2, font=ctk.CTkFont(family=Fonts.FAMILY, size=14), height=36)
        self._address_entry.grid(row=1, column=0, padx=(0, 8), sticky="ew")
        
        self._lbl(row2, "Opening Balance (g)", 0, 1)
        self._balance_entry = ctk.CTkEntry(row2, font=ctk.CTkFont(family=Fonts.FAMILY, size=14), height=36, placeholder_text="0.000")
        self._balance_entry.grid(row=1, column=1, padx=4, sticky="ew")
        
        self._lbl(row2, "Remark", 0, 2)
        self._remark_entry = ctk.CTkEntry(row2, font=ctk.CTkFont(family=Fonts.FAMILY, size=14), height=36)
        self._remark_entry.grid(row=1, column=2, padx=(8, 0), sticky="ew")
        
        # ── Setup Enter Navigation ───────────────────────────────────
        self._setup_enter_navigation()
        
        # Buttons
        btn_frame = ctk.CTkFrame(form_inner, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        buttons = [
            ("➕ Add (Ctrl+S)", self._on_save, theme.ACCENT_GOLD, theme.TEXT_ON_ACCENT),
            ("✏️ Update", self._on_update, theme.ACCENT_BLUE, "white"),
            ("🗑 Delete (Del)", self._on_delete, "#dc2626", "white"),
            ("📄 New (Ctrl+N)", self._on_clear, "transparent", theme.TEXT_PRIMARY),
            ("🚫 Deactivate", self._on_deactivate, "#f97316", "white"),
            ("✅ Reactivate", self._on_reactivate, "#059669", "white"),
        ]
        
        for text, cmd, fg, tc in buttons:
            ctk.CTkButton(
                btn_frame, text=text, command=cmd,
                font=ctk.CTkFont(family=Fonts.FAMILY, size=13, weight="bold"),
                fg_color=fg, text_color=tc,
                border_width=1 if fg == "transparent" else 0,
                height=36, corner_radius=8,
            ).pack(side="left", padx=3)
        
        # Search bar
        search_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        search_frame.pack(side="right")
        
        self._search_entry = ctk.CTkEntry(
            search_frame, font=ctk.CTkFont(family=Fonts.FAMILY, size=11),
            height=34, width=200, placeholder_text="🔍 Search Karigars..."
        )
        self._search_entry.pack(side="left", padx=4)
        self._search_entry.bind("<KeyRelease>", self._on_search)
        
        # ── Table ────────────────────────────────────────────────────
        table_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=12)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(8, 16))
        
        self._table = DataTable(
            table_frame,
            columns=[
                ("id", "ID", 50),
                ("name", "Karigar Name", 150),
                ("phone", "Phone", 110),
                ("city", "City", 100),
                ("opening", "Opening Bal", 90),
                ("issued", "Total Issued", 100),
                ("received", "Total Received", 100),
                ("pending", "Pending", 90),
                ("advance", "Advance", 100),
                ("status", "Status", 80),
                ("active", "Active", 60),
            ],
            on_select=self._on_table_select,
            on_double_click=self._on_table_select,
        )
        self._table.pack(fill="both", expand=True, padx=12, pady=12)
    
    def _lbl(self, parent, text, row, col):
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=12, weight="bold"),
            text_color=self._theme.TEXT_MUTED,
        ).grid(row=row, column=col, sticky="w", padx=4 if col > 0 else 0)
        
    def _setup_enter_navigation(self):
        """Bind Enter key to navigate to the next field."""
        fields = [
            self._name_entry,
            self._phone_entry,
            self._city_entry,
            self._address_entry,
            self._balance_entry,
            self._remark_entry
        ]
        
        for i, field in enumerate(fields):
            widget = field._entry if hasattr(field, "_entry") else field
            if i < len(fields) - 1:
                next_field = fields[i + 1]
                next_widget = next_field._entry if hasattr(next_field, "_entry") else next_field
                widget.bind("<Return>", lambda e, w=next_widget: w.focus_set())
            else:
                widget.bind("<Return>", lambda e: self._on_save())
    
    def _load_table(self, search_term: str = None):
        try:
            if search_term is None:
                search_term = self._search_entry.get() if hasattr(self, '_search_entry') else ""
                
            if search_term:
                karigars = self._karigar_svc.search(search_term)
            else:
                karigars = self._karigar_svc.get_with_balances(include_inactive=True)
            
            data = []
            for k in karigars:
                data.append([
                    k.karigar_id, k.karigar_name, k.phone or "", k.city or "",
                    format_weight(k.opening_balance),
                    format_weight(k.total_issued),
                    format_weight(k.total_received),
                    format_weight(k.pending_silver),
                    format_currency(k.total_advance),
                    k.status,
                    "Yes" if k.is_active else "No",
                ])
            self._table.load_data(data)
        except Exception as e:
            logger.error(f"Failed to load karigars: {e}")
    
    def _on_save(self, event=None):
        from models.karigar import Karigar
        from utils.helpers import safe_float
        
        errors = validate_karigar(self._name_entry.get(), self._phone_entry.get(), self._balance_entry.get() or "0")
        if errors:
            Toast.show(self._app, errors[0].message, "error")
            return
        
        try:
            karigar = Karigar(
                karigar_name=self._name_entry.get().strip(),
                phone=self._phone_entry.get().strip(),
                address=self._address_entry.get().strip(),
                city=self._city_entry.get().strip(),
                opening_balance=safe_float(self._balance_entry.get()),
                remark=self._remark_entry.get().strip(),
            )
            self._karigar_svc.create(karigar)
            Toast.show(self._app, f"Karigar '{karigar.karigar_name}' added!", "success")
            self._on_clear()
            self._load_table()
            
            # Continuous entry: restore focus
            self._name_entry.focus_set()
        except ValueError as e:
            Toast.show(self._app, str(e), "warning")
        except Exception as e:
            Toast.show(self._app, f"Error: {e}", "error")
    
    def _on_update(self, event=None):
        if not self._selected_id:
            Toast.show(self._app, "Select a Karigar to update", "warning")
            return
        
        from models.karigar import Karigar
        from utils.helpers import safe_float
        
        try:
            karigar = Karigar(
                karigar_id=self._selected_id,
                karigar_name=self._name_entry.get().strip(),
                phone=self._phone_entry.get().strip(),
                address=self._address_entry.get().strip(),
                city=self._city_entry.get().strip(),
                opening_balance=safe_float(self._balance_entry.get()),
                remark=self._remark_entry.get().strip(),
                is_active=True,
            )
            self._karigar_svc.update(karigar)
            Toast.show(self._app, "Karigar updated!", "success")
            self._on_clear()
            self._load_table()
        except ValueError as e:
            Toast.show(self._app, str(e), "warning")
        except Exception as e:
            Toast.show(self._app, f"Error: {e}", "error")
    
    def _on_delete(self, event=None):
        if not self._selected_id:
            Toast.show(self._app, "Select a Karigar to delete", "warning")
            return
        if ConfirmationDialog.ask(self._app, "Delete Karigar", "This will permanently delete the Karigar.\nAre you sure?"):
            try:
                self._karigar_svc.delete(self._selected_id)
                Toast.show(self._app, "Karigar deleted", "success")
                self._on_clear()
                self._load_table()
            except ValueError as e:
                Toast.show(self._app, str(e), "warning")
            except Exception as e:
                Toast.show(self._app, f"Error: {e}", "error")
    
    def _on_deactivate(self):
        if not self._selected_id:
            Toast.show(self._app, "Select a Karigar", "warning")
            return
        self._karigar_svc.deactivate(self._selected_id)
        Toast.show(self._app, "Karigar deactivated", "info")
        self._on_clear()
        self._load_table()
    
    def _on_reactivate(self):
        if not self._selected_id:
            Toast.show(self._app, "Select a Karigar", "warning")
            return
        self._karigar_svc.reactivate(self._selected_id)
        Toast.show(self._app, "Karigar reactivated!", "success")
        self._on_clear()
        self._load_table()
    
    def _on_new(self, event=None):
        self._on_clear()
        
    def _on_clear(self, event=None):
        self._selected_id = None
        for entry in [self._name_entry, self._phone_entry, self._city_entry,
                       self._address_entry, self._balance_entry, self._remark_entry]:
            entry.delete(0, "end")
    
    def _on_search(self, event=None):
        term = self._search_entry.get().strip()
        self._load_table(term)
    
    def _on_table_select(self, values):
        if not values:
            return
        self._selected_id = int(values[0])
        karigar = self._karigar_svc.get_by_id(self._selected_id)
        if not karigar:
            return
        
        self._name_entry.delete(0, "end")
        self._name_entry.insert(0, karigar.karigar_name)
        self._phone_entry.delete(0, "end")
        self._phone_entry.insert(0, karigar.phone or "")
        self._city_entry.delete(0, "end")
        self._city_entry.insert(0, karigar.city or "")
        self._address_entry.delete(0, "end")
        self._address_entry.insert(0, karigar.address or "")
        self._balance_entry.delete(0, "end")
        self._balance_entry.insert(0, str(karigar.opening_balance))
        self._remark_entry.delete(0, "end")
        self._remark_entry.insert(0, karigar.remark or "")
