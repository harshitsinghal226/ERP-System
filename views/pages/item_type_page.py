"""
Item Type Management Page — CRUD for silver item categories.
"""

import customtkinter as ctk
import logging

from utils.theme import Fonts, get_theme
from views.components.data_table import DataTable
from views.components.toast import Toast
from views.components.confirmation_dialog import ConfirmationDialog

logger = logging.getLogger(__name__)


class ItemTypePage(ctk.CTkFrame):
    def __init__(self, parent, app):
        theme = get_theme(ctk.get_appearance_mode().lower())
        super().__init__(parent, fg_color=theme.BG_PRIMARY)
        self._app = app
        self._theme = theme
        self._selected_id = None
        
        from repositories.item_type_repository import ItemTypeRepository
        self._repo = ItemTypeRepository()
        
        self._build_ui()
        self._load_table()
    
    def _build_ui(self):
        theme = self._theme
        
        form_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=12)
        form_frame.pack(fill="x", padx=20, pady=(16, 8))
        
        form_inner = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_inner.pack(fill="x", padx=20, pady=16)
        # Row 1: Name and Description
        row1 = ctk.CTkFrame(form_inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 12))
        row1.grid_columnconfigure(0, weight=1, uniform="f")
        row1.grid_columnconfigure(1, weight=2, uniform="f")
        
        ctk.CTkLabel(
            row1, text="Item Name *",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=12, weight="bold"),
            text_color=theme.TEXT_MUTED,
        ).grid(row=0, column=0, sticky="w")
        self._name_entry = ctk.CTkEntry(row1, font=ctk.CTkFont(family=Fonts.FAMILY, size=14), height=36)
        self._name_entry.grid(row=1, column=0, padx=(0, 8), sticky="ew")
        
        ctk.CTkLabel(
            row1, text="Description",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=12, weight="bold"),
            text_color=theme.TEXT_MUTED,
        ).grid(row=0, column=1, sticky="w")
        self._desc_entry = ctk.CTkEntry(row1, font=ctk.CTkFont(family=Fonts.FAMILY, size=14), height=36)
        self._desc_entry.grid(row=1, column=1, sticky="ew")
        
        # ── Setup Enter Navigation ───────────────────────────────────
        self._setup_enter_navigation()
        
        btn_frame = ctk.CTkFrame(form_inner, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        buttons = [
            ("➕ Add (Ctrl+S)", self._on_save, theme.ACCENT_GOLD, theme.TEXT_ON_ACCENT),
            ("✏️ Update", self._on_update, theme.ACCENT_BLUE, "white"),
            ("🗑 Delete (Del)", self._on_delete, "#dc2626", "white"),
            ("📄 New (Ctrl+N)", self._on_clear, "transparent", theme.TEXT_PRIMARY),
            ("🚫 Disable", self._on_disable, "#f97316", "white"),
            ("✅ Enable", self._on_enable, "#059669", "white"),
        ]
        
        for text, cmd, fg, tc in buttons:
            ctk.CTkButton(
                btn_frame, text=text, command=cmd,
                font=ctk.CTkFont(family=Fonts.FAMILY, size=13, weight="bold"),
                fg_color=fg, text_color=tc,
                border_width=1 if fg == "transparent" else 0,
                height=36, corner_radius=8,
            ).pack(side="left", padx=3)
        
        # Search
        self._search = ctk.CTkEntry(btn_frame, height=34, width=200, placeholder_text="🔍 Search...")
        self._search.pack(side="right", padx=4)
        self._search.bind("<KeyRelease>", lambda e: self._load_table(self._search.get()))
        
        # Table
        table_frame = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=12)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(8, 16))
        
        self._table = DataTable(
            table_frame,
            columns=[
                ("id", "ID", 50), ("name", "Item Name", 200),
                ("desc", "Description", 300), ("status", "Status", 80),
            ],
            on_select=self._on_select,
        )
        self._table.pack(fill="both", expand=True, padx=12, pady=12)
        
    def _setup_enter_navigation(self):
        """Bind Enter key to navigate to the next field."""
        self._name_entry.bind("<Return>", lambda e: self._desc_entry.focus_set())
        self._desc_entry.bind("<Return>", lambda e: self._on_save())
    
    def _load_table(self, search: str = None):
        try:
            if search is None:
                search = self._search.get() if hasattr(self, '_search') else ""
                
            if search:
                items = self._repo.search(search)
            else:
                items = self._repo.get_all(include_inactive=True)
            data = [[it.item_type_id, it.item_name, it.description or "", "Active" if it.is_active else "Disabled"] for it in items]
            self._table.load_data(data)
        except Exception as e:
            logger.error(f"Failed to load items: {e}")
    
    def _on_save(self, event=None):
        name = self._name_entry.get().strip()
        if not name:
            Toast.show(self._app, "Item Name is required", "error")
            return
        if self._repo.name_exists(name):
            Toast.show(self._app, f"'{name}' already exists", "warning")
            return
        
        from models.item_type import ItemType
        self._repo.create(ItemType(item_name=name, description=self._desc_entry.get().strip()))
        Toast.show(self._app, f"Item Type '{name}' added!", "success")
        self._on_clear()
        self._load_table()
        
        # Restore focus
        self._name_entry.focus_set()
    
    def _on_update(self, event=None):
        if not self._selected_id:
            Toast.show(self._app, "Select an item to update", "warning")
            return
        from models.item_type import ItemType
        self._repo.update(ItemType(item_type_id=self._selected_id, item_name=self._name_entry.get().strip(), description=self._desc_entry.get().strip(), is_active=True))
        Toast.show(self._app, "Item Type updated!", "success")
        self._on_clear()
        self._load_table()
    
    def _on_delete(self, event=None):
        if not self._selected_id:
            Toast.show(self._app, "Select an item to delete", "warning")
            return
        if ConfirmationDialog.ask(self._app, "Delete Item Type", "Are you sure?"):
            self._repo.delete(self._selected_id)
            Toast.show(self._app, "Item Type deleted", "success")
            self._on_clear()
            self._load_table()
    
    def _on_disable(self):
        if self._selected_id:
            self._repo.deactivate(self._selected_id)
            Toast.show(self._app, "Item Type disabled", "info")
            self._on_clear()
            self._load_table()
    
    def _on_enable(self):
        if self._selected_id:
            self._repo.reactivate(self._selected_id)
            Toast.show(self._app, "Item Type enabled!", "success")
            self._on_clear()
            self._load_table()
    
    def _on_new(self, event=None):
        self._on_clear()
        
    def _on_clear(self, event=None):
        self._selected_id = None
        self._name_entry.delete(0, "end")
        self._desc_entry.delete(0, "end")
    
    def _on_select(self, values):
        if values:
            self._selected_id = int(values[0])
            self._name_entry.delete(0, "end")
            self._name_entry.insert(0, str(values[1]))
            self._desc_entry.delete(0, "end")
            self._desc_entry.insert(0, str(values[2]))
