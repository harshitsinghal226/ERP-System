"""
Dashboard Page — Home page with stat cards and navigation cards.
"""

import customtkinter as ctk
import logging

from utils.theme import Colors, Fonts, Spacing, Dimensions, get_theme
from utils.helpers import format_weight, format_currency
from utils.constants import (
    NAV_ISSUE, NAV_RECEIVE, NAV_KARIGAR, NAV_REPORTS,
    NAV_SEARCH, NAV_BACKUP, NAV_SETTINGS
)

logger = logging.getLogger(__name__)


class DashboardPage(ctk.CTkFrame):
    """Home dashboard with statistics and quick navigation."""
    
    def __init__(self, parent, app):
        theme = get_theme(ctk.get_appearance_mode().lower())
        super().__init__(parent, fg_color=theme.BG_PRIMARY)
        
        self._app = app
        self._theme = theme
        
        # Scrollable container
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24, pady=16)
        
        # Load stats
        stats = self._load_stats()
        
        # ── Statistics Cards ──────────────────────────────────────────
        stats_label = ctk.CTkLabel(
            scroll, text="Overview",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=16, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        )
        stats_label.pack(fill="x", pady=(0, 12))
        
        stats_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        stats_grid.pack(fill="x", pady=(0, 24))
        
        # Configure grid columns
        for i in range(6):
            stats_grid.grid_columnconfigure(i, weight=1, uniform="stat")
        
        stat_cards = [
            ("Total Karigars", str(stats.get("total_karigars", 0)), "👤", theme.ACCENT_BLUE),
            ("Total Issued", format_weight(stats.get("total_issued", 0)) + "g", "📤", theme.ACCENT_GOLD),
            ("Total Received", format_weight(stats.get("total_received", 0)) + "g", "📥", "#34d399"),
            ("Pending Silver", format_weight(stats.get("pending_silver", 0)) + "g", "⏳", "#f87171"),
            ("Today's Issue", format_weight(stats.get("today_issued", 0)) + "g", "📆", "#a78bfa"),
            ("Total Advance", format_currency(stats.get("total_advance", 0)), "💰", "#fbbf24"),
        ]
        
        for i, (label, value, icon, color) in enumerate(stat_cards):
            self._create_stat_card(stats_grid, label, value, icon, color, i)
        
        # ── Quick Navigation Cards ───────────────────────────────────
        ctk.CTkFrame(scroll, height=1, fg_color=theme.BORDER).pack(fill="x", pady=(8, 16))
        
        nav_label = ctk.CTkLabel(
            scroll, text="Quick Actions",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=16, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        )
        nav_label.pack(fill="x", pady=(0, 12))
        
        nav_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        nav_grid.pack(fill="x")
        
        for i in range(4):
            nav_grid.grid_columnconfigure(i, weight=1, uniform="nav")
        
        nav_cards = [
            ("Issue Entry", "Record silver issued to Karigar", "📤", NAV_ISSUE, theme.ACCENT_GOLD),
            ("Receive Entry", "Record silver received from Karigar", "📥", NAV_RECEIVE, "#34d399"),
            ("Karigar Management", "Add, edit, manage Karigars", "👤", NAV_KARIGAR, theme.ACCENT_BLUE),
            ("Reports", "Generate and export reports", "📊", NAV_REPORTS, "#a78bfa"),
            ("Search Records", "Find any record quickly", "🔍", NAV_SEARCH, "#60a5fa"),
            ("Backup & Archive", "Monthly backup and archive", "💾", NAV_BACKUP, "#fbbf24"),
            ("Settings", "Configure application settings", "⚙️", NAV_SETTINGS, "#9ca3b4"),
        ]
        
        for i, (title, subtitle, icon, nav_id, color) in enumerate(nav_cards):
            row = i // 4
            col = i % 4
            self._create_nav_card(nav_grid, title, subtitle, icon, nav_id, color, row, col)
        
        # ── Today's Activity ──────────────────────────────────────────
        ctk.CTkFrame(scroll, height=1, fg_color=theme.BORDER).pack(fill="x", pady=(24, 16))
        
        today_label = ctk.CTkLabel(
            scroll, text="Today's Activity",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=16, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        )
        today_label.pack(fill="x", pady=(0, 12))
        
        today_frame = ctk.CTkFrame(scroll, fg_color=theme.BG_SECONDARY, corner_radius=12)
        today_frame.pack(fill="x", pady=(0, 16))
        
        today_inner = ctk.CTkFrame(today_frame, fg_color="transparent")
        today_inner.pack(fill="x", padx=20, pady=16)
        
        today_issued = format_weight(stats.get("today_issued", 0))
        today_received = format_weight(stats.get("today_received", 0))
        
        ctk.CTkLabel(
            today_inner,
            text=f"📤 Issued Today: {today_issued}g     |     📥 Received Today: {today_received}g",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=13),
            text_color=theme.TEXT_SECONDARY,
        ).pack()
    
    def _create_stat_card(self, parent, label, value, icon, color, col):
        """Create a dashboard stat card."""
        theme = self._theme
        
        card = ctk.CTkFrame(
            parent,
            fg_color=theme.BG_SECONDARY,
            corner_radius=12,
            border_width=1,
            border_color=theme.BORDER,
        )
        card.grid(row=0, column=col, padx=6, pady=4, sticky="nsew")
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=14)
        
        # Icon + label row
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        
        ctk.CTkLabel(
            top, text=icon,
            font=ctk.CTkFont(size=20),
        ).pack(side="left")
        
        ctk.CTkLabel(
            top, text=label,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=10),
            text_color=theme.TEXT_MUTED,
        ).pack(side="left", padx=(6, 0))
        
        # Value
        ctk.CTkLabel(
            inner, text=value,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=22, weight="bold"),
            text_color=color,
            anchor="w",
        ).pack(fill="x", pady=(8, 0))
    
    def _create_nav_card(self, parent, title, subtitle, icon, nav_id, color, row, col):
        """Create a navigation card button."""
        theme = self._theme
        
        card = ctk.CTkFrame(
            parent,
            fg_color=theme.BG_SECONDARY,
            corner_radius=12,
            border_width=1,
            border_color=theme.BORDER,
            cursor="hand2",
        )
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=18)
        
        # Icon
        ctk.CTkLabel(
            inner, text=icon,
            font=ctk.CTkFont(size=32),
        ).pack(anchor="w")
        
        # Title
        ctk.CTkLabel(
            inner, text=title,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=14, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        ).pack(fill="x", pady=(8, 2))
        
        # Subtitle
        ctk.CTkLabel(
            inner, text=subtitle,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=10),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).pack(fill="x")
        
        # Make entire card clickable
        for widget in [card, inner] + list(inner.winfo_children()):
            widget.bind("<Button-1>", lambda e, nid=nav_id: self._app.navigate_to(nid))
            widget.bind("<Enter>", lambda e, c=card: c.configure(
                border_color=color, fg_color=theme.BG_TERTIARY
            ))
            widget.bind("<Leave>", lambda e, c=card: c.configure(
                border_color=theme.BORDER, fg_color=theme.BG_SECONDARY
            ))
    
    def _load_stats(self) -> dict:
        """Load dashboard statistics from the database."""
        try:
            from services.report_service import ReportService
            service = ReportService()
            return service.get_dashboard_stats()
        except Exception as e:
            logger.warning(f"Could not load dashboard stats: {e}")
            return {
                "total_karigars": 0, "total_issued": 0, "total_received": 0,
                "pending_silver": 0, "today_issued": 0, "today_received": 0,
                "total_advance": 0,
            }
