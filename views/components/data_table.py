"""
Reusable data table component using ttk.Treeview with professional styling.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from typing import List, Tuple, Optional, Callable

from utils.theme import Colors, Fonts, get_theme


class DataTable(ctk.CTkFrame):
    """
    A professional data table with:
    - Column sorting
    - Alternating row colors
    - Selection highlighting
    - Scrollbars
    - Double-click to edit callback
    """
    
    def __init__(self, parent, columns: List[Tuple[str, str, int]], 
                 on_select: Callable = None,
                 on_double_click: Callable = None,
                 show_scrollbar: bool = True,
                 height: int = 15):
        """
        Args:
            parent: Parent widget
            columns: List of (column_id, display_name, width) tuples
            on_select: Callback when row is selected → fn(item_values)
            on_double_click: Callback on double-click → fn(item_values)
            height: Number of visible rows
        """
        super().__init__(parent, fg_color="transparent")
        
        self._columns = columns
        self._on_select = on_select
        self._on_double_click = on_double_click
        self._sort_column = None
        self._sort_reverse = False
        
        # Style the treeview
        self._setup_style()
        
        # Create treeview
        col_ids = [c[0] for c in columns]
        self._tree = ttk.Treeview(
            self,
            columns=col_ids,
            show="headings",
            height=height,
            style="Custom.Treeview",
            selectmode="browse",
        )
        
        # Configure columns
        for col_id, display_name, width in columns:
            self._tree.heading(
                col_id, text=display_name,
                command=lambda c=col_id: self._sort_by(c)
            )
            self._tree.column(col_id, width=width, minwidth=50)
        
        # Scrollbars
        if show_scrollbar:
            y_scroll = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
            x_scroll = ttk.Scrollbar(self, orient="horizontal", command=self._tree.xview)
            self._tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
            
            self._tree.grid(row=0, column=0, sticky="nsew")
            y_scroll.grid(row=0, column=1, sticky="ns")
            x_scroll.grid(row=1, column=0, sticky="ew")
        else:
            self._tree.pack(fill="both", expand=True)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Events
        self._tree.bind("<<TreeviewSelect>>", self._on_row_select)
        self._tree.bind("<Double-1>", self._on_row_double_click)
    
    def _setup_style(self):
        """Configure ttk Treeview styling for a professional look."""
        style = ttk.Style()
        
        theme = get_theme(ctk.get_appearance_mode().lower())
        
        style.configure("Custom.Treeview",
            background=theme.BG_SECONDARY,
            foreground=theme.TEXT_PRIMARY,
            fieldbackground=theme.BG_SECONDARY,
            rowheight=32,
            font=(Fonts.FAMILY, Fonts.SIZE_SMALL),
            borderwidth=0,
        )
        
        style.configure("Custom.Treeview.Heading",
            background=theme.TABLE_HEADER,
            foreground=theme.TEXT_PRIMARY,
            font=(Fonts.FAMILY, Fonts.SIZE_SMALL, "bold"),
            borderwidth=0,
            relief="flat",
        )
        
        style.map("Custom.Treeview",
            background=[("selected", theme.TABLE_SELECTED)],
            foreground=[("selected", theme.TEXT_PRIMARY)],
        )
        
        style.map("Custom.Treeview.Heading",
            background=[("active", theme.BG_HOVER)],
        )
        
        # Configure tag colors for alternating rows
        style.configure("Custom.Treeview", 
            background=theme.BG_SECONDARY)
    
    def load_data(self, data: List[List], tags_map: dict = None):
        """
        Load data into the table, clearing existing rows.
        
        Args:
            data: List of rows, each row is a list of values
            tags_map: Optional dict mapping row index to tag name for coloring
        """
        # Clear existing
        self._tree.delete(*self._tree.get_children())
        
        theme = get_theme(ctk.get_appearance_mode().lower())
        
        # Configure alternating row tags
        self._tree.tag_configure("even", background=theme.BG_SECONDARY)
        self._tree.tag_configure("odd", background=theme.TABLE_ROW_ALT)
        self._tree.tag_configure("naam", foreground="#f87171")    # Red for Naam
        self._tree.tag_configure("jama", foreground="#34d399")    # Green for Jama
        self._tree.tag_configure("issue", foreground="#fbbf24")   # Yellow for Issue
        self._tree.tag_configure("receive", foreground="#60a5fa") # Blue for Receive
        
        for i, row in enumerate(data):
            tag = "even" if i % 2 == 0 else "odd"
            
            # Apply custom tag if provided
            if tags_map and i in tags_map:
                tag = tags_map[i]
            
            self._tree.insert("", "end", values=row, tags=(tag,))
    
    def clear(self):
        """Remove all rows."""
        self._tree.delete(*self._tree.get_children())
    
    def get_selected(self) -> Optional[Tuple]:
        """Get the values of the currently selected row."""
        selected = self._tree.selection()
        if selected:
            return self._tree.item(selected[0])["values"]
        return None
    
    def get_selected_index(self) -> Optional[int]:
        """Get the index of the selected row."""
        selected = self._tree.selection()
        if selected:
            return self._tree.index(selected[0])
        return None
    
    def select_row(self, index: int):
        """Programmatically select a row by index."""
        children = self._tree.get_children()
        if 0 <= index < len(children):
            self._tree.selection_set(children[index])
            self._tree.see(children[index])
    
    def get_row_count(self) -> int:
        """Get total number of rows."""
        return len(self._tree.get_children())
    
    def _on_row_select(self, event):
        """Handle row selection."""
        if self._on_select:
            values = self.get_selected()
            if values:
                self._on_select(values)
    
    def _on_row_double_click(self, event):
        """Handle double-click on a row."""
        if self._on_double_click:
            values = self.get_selected()
            if values:
                self._on_double_click(values)
    
    def _sort_by(self, column: str):
        """Sort table by the clicked column header."""
        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False
        
        # Get all data
        items = [(self._tree.set(child, column), child) 
                 for child in self._tree.get_children()]
        
        # Try numeric sort, fallback to string
        try:
            items.sort(key=lambda t: float(t[0]), reverse=self._sort_reverse)
        except ValueError:
            items.sort(key=lambda t: t[0].lower(), reverse=self._sort_reverse)
        
        for index, (_, child) in enumerate(items):
            self._tree.move(child, "", index)
            # Reapply alternating colors
            tag = "even" if index % 2 == 0 else "odd"
            self._tree.item(child, tags=(tag,))
