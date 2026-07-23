"""
Main Application Window — The root UI with sidebar navigation and page routing.
This is the central hub that manages all pages and navigation.
"""

import customtkinter as ctk
import tkinter as tk
import sys
import logging
import os

from config.app_config import (
    APP_TITLE, APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT, SIDEBAR_WIDTH,
    ensure_directories, DB_PATH, ICONS_DIR
)
from utils.theme import Colors, Fonts, Spacing, Dimensions, get_theme
from utils.constants import (
    NAV_DASHBOARD, NAV_ISSUE, NAV_RECEIVE, NAV_KARIGAR,
    NAV_ITEM_TYPE, NAV_SEARCH, NAV_REPORTS, NAV_BACKUP, NAV_SETTINGS
)
from views.components.toast import Toast

logger = logging.getLogger(__name__)


# ── Navigation Item Configuration ─────────────────────────────────────
NAV_ITEMS = [
    {"id": NAV_DASHBOARD,  "label": "Dashboard",          "icon": "🏠"},
    {"id": NAV_ISSUE,      "label": "Issue Entry",        "icon": "📤"},
    {"id": NAV_RECEIVE,    "label": "Receive Entry",      "icon": "📥"},
    {"id": NAV_KARIGAR,    "label": "Karigar Management",  "icon": "👤"},
    {"id": NAV_ITEM_TYPE,  "label": "Item Types",         "icon": "📋"},
    {"id": NAV_SEARCH,     "label": "Search Records",     "icon": "🔍"},
    {"id": NAV_REPORTS,    "label": "Reports",             "icon": "📊"},
    {"id": NAV_BACKUP,     "label": "Backup & Archive",   "icon": "💾"},
    {"id": NAV_SETTINGS,   "label": "Settings",           "icon": "⚙️"},
]


class MainApplication(ctk.CTk):
    """Root application window with sidebar navigation."""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        
        # Set App Icon
        icon_path = os.path.join(ICONS_DIR, "app_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                logger.warning(f"Could not load app icon: {e}")
        
        # Start maximized
        self.state("zoomed")
        
        # Theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self._current_page = None
        self._pages = {}
        self._nav_buttons = {}
        
        # Build UI
        self._build_layout()
        self._build_sidebar()
        self._build_header()
        self._build_content_area()
        
        # Show dashboard
        self.navigate_to(NAV_DASHBOARD)
        
        # Keyboard shortcuts
        self.bind("<Alt-h>", lambda e: self.navigate_to(NAV_DASHBOARD))
        self.bind("<Control-s>", self._handle_shortcut_save)
        self.bind("<Control-u>", self._handle_shortcut_update)
        self.bind("<Control-n>", self._handle_shortcut_new)
        self.bind("<Delete>", self._handle_shortcut_delete)
        
        self.bind("<Alt-F4>", lambda e: self._on_exit())
        self.protocol("WM_DELETE_WINDOW", self._on_exit)
    
    def _build_layout(self):
        """Set up the main grid layout."""
        self.grid_rowconfigure(1, weight=1)    # Content row expands
        self.grid_columnconfigure(1, weight=1)  # Content column expands
    
    def _build_sidebar(self):
        """Build the navigation sidebar."""
        theme = get_theme(ctk.get_appearance_mode().lower())
        
        self._sidebar = ctk.CTkFrame(
            self, 
            width=SIDEBAR_WIDTH,
            corner_radius=0,
            fg_color=theme.SIDEBAR_BG,
        )
        self._sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self._sidebar.grid_propagate(False)
        
        # ── Logo / Company Name ───────────────────────────────────────
        logo_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent", height=80)
        logo_frame.pack(fill="x", padx=16, pady=(20, 8))
        logo_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            logo_frame,
            text="✦",
            font=ctk.CTkFont(size=28),
            text_color=theme.ACCENT_GOLD,
        ).pack(pady=(4, 0))
        
        ctk.CTkLabel(
            logo_frame,
            text=APP_NAME,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=15, weight="bold"),
            text_color=theme.ACCENT_GOLD,
        ).pack()
        
        ctk.CTkLabel(
            logo_frame,
            text="Silver Manufacturing",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=9),
            text_color=theme.TEXT_MUTED,
        ).pack()
        
        # Divider
        ctk.CTkFrame(self._sidebar, height=1, fg_color=theme.BORDER).pack(
            fill="x", padx=20, pady=(12, 8)
        )
        
        # ── Navigation Buttons ────────────────────────────────────────
        nav_container = ctk.CTkScrollableFrame(
            self._sidebar,
            fg_color="transparent",
            scrollbar_button_color=theme.BG_TERTIARY,
        )
        nav_container.pack(fill="both", expand=True, padx=8, pady=4)
        
        for item in NAV_ITEMS:
            btn = self._create_nav_button(nav_container, item, theme)
            self._nav_buttons[item["id"]] = btn
        
        # ── Exit Button at Bottom ─────────────────────────────────────
        ctk.CTkFrame(self._sidebar, height=1, fg_color=theme.BORDER).pack(
            fill="x", padx=20, pady=(4, 8)
        )
        
        exit_btn = ctk.CTkButton(
            self._sidebar,
            text="  🚪  Exit Application",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=12),
            fg_color="transparent",
            text_color="#f87171",
            hover_color=theme.SIDEBAR_HOVER,
            anchor="w",
            height=40,
            corner_radius=8,
            command=self._on_exit,
        )
        exit_btn.pack(fill="x", padx=12, pady=(0, 16))
    
    def _create_nav_button(self, parent, item: dict, theme) -> ctk.CTkButton:
        """Create a single navigation button."""
        btn = ctk.CTkButton(
            parent,
            text=f"  {item['icon']}  {item['label']}",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=12),
            fg_color="transparent",
            text_color=theme.TEXT_SECONDARY,
            hover_color=theme.SIDEBAR_HOVER,
            anchor="w",
            height=40,
            corner_radius=8,
            command=lambda nav_id=item["id"]: self.navigate_to(nav_id),
        )
        btn.pack(fill="x", pady=2)
        return btn
    
    def _build_header(self):
        """Build the top header bar."""
        theme = get_theme(ctk.get_appearance_mode().lower())
        
        self._header = ctk.CTkFrame(
            self, height=56, corner_radius=0,
            fg_color=theme.BG_SECONDARY,
            border_width=0,
        )
        self._header.grid(row=0, column=1, sticky="new")
        self._header.grid_propagate(False)
        
        # Page title (updated on navigation)
        self._page_title_label = ctk.CTkLabel(
            self._header,
            text="Dashboard",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=18, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
        )
        self._page_title_label.pack(side="left", padx=24, pady=12)
        
        # Right side — theme toggle
        right_frame = ctk.CTkFrame(self._header, fg_color="transparent")
        right_frame.pack(side="right", padx=16)
        
        self._theme_btn = ctk.CTkButton(
            right_frame,
            text="🌙",
            width=36, height=36,
            corner_radius=18,
            fg_color=theme.BG_TERTIARY,
            hover_color=theme.BG_HOVER,
            command=self._toggle_theme,
            font=ctk.CTkFont(size=16),
        )
        self._theme_btn.pack(side="right", padx=4)
    
    def _build_content_area(self):
        """Build the main content area where pages are displayed."""
        theme = get_theme(ctk.get_appearance_mode().lower())
        
        self._content = ctk.CTkFrame(
            self, 
            corner_radius=0,
            fg_color=theme.BG_PRIMARY,
        )
        self._content.grid(row=1, column=1, sticky="nsew")
    
    def navigate_to(self, page_id: str):
        """Navigate to a page by its ID."""
        # Update sidebar active state
        theme = get_theme(ctk.get_appearance_mode().lower())
        
        for nav_id, btn in self._nav_buttons.items():
            if nav_id == page_id:
                btn.configure(
                    fg_color=theme.SIDEBAR_ACTIVE,
                    text_color=theme.ACCENT_GOLD,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=theme.TEXT_SECONDARY,
                )
        
        # Update header title
        title_map = {
            NAV_DASHBOARD: "Dashboard",
            NAV_ISSUE: "Issue Entry — Silver to Karigar",
            NAV_RECEIVE: "Receive Entry — Silver from Karigar",
            NAV_KARIGAR: "Karigar Management",
            NAV_ITEM_TYPE: "Item Type Management",
            NAV_SEARCH: "Search Records",
            NAV_REPORTS: "Reports",
            NAV_BACKUP: "Backup & Archive",
            NAV_SETTINGS: "Settings",
        }
        self._page_title_label.configure(text=title_map.get(page_id, ""))
        
        # Clear content area
        for widget in self._content.winfo_children():
            widget.destroy()
        
        # Load page
        page = self._get_page(page_id)
        if page:
            page.pack(fill="both", expand=True, padx=0, pady=0)
            self._current_page = page_id
            self._current_page_instance = page
    
    def _get_page(self, page_id: str):
        """Lazy-load and return the requested page."""
        try:
            if page_id == NAV_DASHBOARD:
                from views.pages.dashboard_page import DashboardPage
                return DashboardPage(self._content, self)
            elif page_id == NAV_ISSUE:
                from views.pages.issue_page import IssuePage
                return IssuePage(self._content, self)
            elif page_id == NAV_RECEIVE:
                from views.pages.receive_page import ReceivePage
                return ReceivePage(self._content, self)
            elif page_id == NAV_KARIGAR:
                from views.pages.karigar_page import KarigarPage
                return KarigarPage(self._content, self)
            elif page_id == NAV_ITEM_TYPE:
                from views.pages.item_type_page import ItemTypePage
                return ItemTypePage(self._content, self)
            elif page_id == NAV_SEARCH:
                from views.pages.search_page import SearchPage
                return SearchPage(self._content, self)
            elif page_id == NAV_REPORTS:
                from views.pages.report_page import ReportPage
                return ReportPage(self._content, self)
            elif page_id == NAV_BACKUP:
                from views.pages.backup_page import BackupPage
                return BackupPage(self._content, self)
            elif page_id == NAV_SETTINGS:
                from views.pages.settings_page import SettingsPage
                return SettingsPage(self._content, self)
        except Exception as e:
            logger.error(f"Failed to load page {page_id}: {e}")
            return self._error_page(str(e))
    
    def _error_page(self, message: str):
        """Show an error page when a module fails to load."""
        frame = ctk.CTkFrame(self._content, fg_color="transparent")
        ctk.CTkLabel(
            frame, text="⚠ Error Loading Page",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#f87171",
        ).pack(pady=(80, 16))
        ctk.CTkLabel(
            frame, text=message,
            font=ctk.CTkFont(size=12),
            text_color="#9ca3b4",
            wraplength=600,
        ).pack()
        return frame
    
    def show_toast(self, message: str, toast_type: str = "success"):
        """Show a toast notification."""
        Toast.show(self, message, toast_type)
    
    def _toggle_theme(self):
        """Toggle between dark and light mode."""
        current = ctk.get_appearance_mode()
        new_mode = "light" if current.lower() == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        self._theme_btn.configure(text="☀️" if new_mode == "dark" else "🌙")
        
        theme = get_theme(new_mode)
        
        # Update sidebar
        self._sidebar.configure(fg_color=theme.SIDEBAR_BG)
        for widget in self._sidebar.winfo_children():
            # Logo frame labels
            if isinstance(widget, ctk.CTkFrame) and widget.cget("fg_color") == "transparent":
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        text = child.cget("text")
                        if text == "✦" or text == APP_NAME:
                            child.configure(text_color=theme.ACCENT_GOLD)
                        elif text == "Silver Manufacturing":
                            child.configure(text_color=theme.TEXT_MUTED)
            # Dividers
            elif isinstance(widget, ctk.CTkFrame) and widget.winfo_height() == 1:
                widget.configure(fg_color=theme.BORDER)
        
        # Update Nav buttons container
        nav_container = self._sidebar.winfo_children()[2]
        if isinstance(nav_container, ctk.CTkScrollableFrame):
            nav_container.configure(scrollbar_button_color=theme.BG_TERTIARY)
            
        # Exit button text color
        exit_btn = self._sidebar.winfo_children()[-1]
        if isinstance(exit_btn, ctk.CTkButton):
            exit_btn.configure(hover_color=theme.SIDEBAR_HOVER)
        
        # Update Header
        self._header.configure(fg_color=theme.BG_SECONDARY)
        self._page_title_label.configure(text_color=theme.TEXT_PRIMARY)
        self._theme_btn.configure(
            fg_color=theme.BG_TERTIARY,
            hover_color=theme.BG_HOVER
        )
        
        # Update content area
        self._content.configure(fg_color=theme.BG_PRIMARY)
        
        # Refresh current page
        if self._current_page:
            self.navigate_to(self._current_page)
    
    def _on_exit(self):
        """Handle application exit."""
        self.destroy()
        sys.exit(0)
        
    def _handle_shortcut_save(self, event=None):
        if hasattr(self, '_current_page_instance') and hasattr(self._current_page_instance, "_on_save"):
            self._current_page_instance._on_save()
            
    def _handle_shortcut_update(self, event=None):
        if hasattr(self, '_current_page_instance') and hasattr(self._current_page_instance, "_on_update"):
            self._current_page_instance._on_update()
            
    def _handle_shortcut_new(self, event=None):
        if hasattr(self, '_current_page_instance') and hasattr(self._current_page_instance, "_on_new"):
            self._current_page_instance._on_new()
            
    def _handle_shortcut_delete(self, event=None):
        if hasattr(self, '_current_page_instance') and hasattr(self._current_page_instance, "_on_delete"):
            self._current_page_instance._on_delete()
