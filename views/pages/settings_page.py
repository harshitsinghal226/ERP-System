"""
Settings Page — Company info, paths, theme, printer configuration.
"""

import customtkinter as ctk
import logging

from utils.theme import Fonts, get_theme
from views.components.toast import Toast

logger = logging.getLogger(__name__)


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        theme = get_theme(ctk.get_appearance_mode().lower())
        super().__init__(parent, fg_color=theme.BG_PRIMARY)
        self._app = app
        self._theme = theme
        
        from repositories.settings_repository import SettingsRepository
        self._settings_repo = SettingsRepository()
        
        self._build_ui()
        self._load_settings()
    
    def _build_ui(self):
        theme = self._theme
        
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=16)
        
        # ── Company Information ──────────────────────────────────────
        self._section(scroll, "🏢 Company Information")
        
        company_frame = ctk.CTkFrame(scroll, fg_color=theme.BG_SECONDARY, corner_radius=12)
        company_frame.pack(fill="x", pady=(0, 16))
        ci = ctk.CTkFrame(company_frame, fg_color="transparent")
        ci.pack(fill="x", padx=20, pady=16)
        
        for i in range(2):
            ci.grid_columnconfigure(i, weight=1, uniform="s")
        
        self._company_name = self._field(ci, "Company Name", 0, 0)
        self._company_phone = self._field(ci, "Phone", 0, 1)
        self._company_address = self._field(ci, "Address", 2, 0)
        self._company_gst = self._field(ci, "GST Number", 2, 1)
        
        # ── Paths ────────────────────────────────────────────────────
        self._section(scroll, "📁 File Paths")
        
        path_frame = ctk.CTkFrame(scroll, fg_color=theme.BG_SECONDARY, corner_radius=12)
        path_frame.pack(fill="x", pady=(0, 16))
        pi = ctk.CTkFrame(path_frame, fg_color="transparent")
        pi.pack(fill="x", padx=20, pady=16)
        pi.grid_columnconfigure(0, weight=1)
        
        self._db_path = self._field(pi, "Database Location", 0, 0, colspan=1)
        self._backup_path = self._field(pi, "Backup Folder", 2, 0, colspan=1)
        
        # ── Display ──────────────────────────────────────────────────
        self._section(scroll, "🎨 Display & Preferences")
        
        display_frame = ctk.CTkFrame(scroll, fg_color=theme.BG_SECONDARY, corner_radius=12)
        display_frame.pack(fill="x", pady=(0, 16))
        di = ctk.CTkFrame(display_frame, fg_color="transparent")
        di.pack(fill="x", padx=20, pady=16)
        
        ctk.CTkLabel(di, text="Theme", font=ctk.CTkFont(family=Fonts.FAMILY, size=10, weight="bold"), text_color=theme.TEXT_MUTED).pack(anchor="w")
        self._theme_combo = ctk.CTkComboBox(di, values=["dark", "light"], height=36, width=200, state="readonly")
        self._theme_combo.pack(anchor="w", pady=(4, 8))
        
        ctk.CTkLabel(di, text="Weight Decimals", font=ctk.CTkFont(family=Fonts.FAMILY, size=10, weight="bold"), text_color=theme.TEXT_MUTED).pack(anchor="w")
        self._decimals_combo = ctk.CTkComboBox(di, values=["2", "3", "4"], height=36, width=200, state="readonly")
        self._decimals_combo.pack(anchor="w", pady=(4, 8))
        
        # ── Save Button ──────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(8, 16))
        
        ctk.CTkButton(
            btn_frame, text="💾 Save Settings",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=13, weight="bold"),
            fg_color=theme.ACCENT_GOLD, text_color=theme.TEXT_ON_ACCENT,
            height=42, width=180, corner_radius=8,
            command=self._on_save,
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame, text="↩ Reset to Defaults",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=12),
            fg_color="transparent", border_width=1,
            height=42, width=160, corner_radius=8,
            command=self._on_reset,
        ).pack(side="left", padx=8)
    
    def _section(self, parent, text):
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=14, weight="bold"),
            text_color=self._theme.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(8, 6))
    
    def _field(self, parent, label, row, col, colspan=1):
        theme = self._theme
        ctk.CTkLabel(
            parent, text=label,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=10, weight="bold"),
            text_color=theme.TEXT_MUTED,
        ).grid(row=row, column=col, columnspan=colspan, sticky="w", padx=4)
        
        entry = ctk.CTkEntry(parent, font=ctk.CTkFont(family=Fonts.FAMILY, size=12), height=36)
        entry.grid(row=row + 1, column=col, columnspan=colspan, sticky="ew", padx=4, pady=(0, 8))
        return entry
    
    def _load_settings(self):
        try:
            settings = self._settings_repo.get_all_as_dict()
            
            self._company_name.insert(0, settings.get("company_name", "Aashu Jewellers"))
            self._company_phone.insert(0, settings.get("company_phone", ""))
            self._company_address.insert(0, settings.get("company_address", ""))
            self._company_gst.insert(0, settings.get("company_gst", ""))
            self._db_path.insert(0, settings.get("database_location", ""))
            self._backup_path.insert(0, settings.get("backup_folder", ""))
            self._theme_combo.set(settings.get("theme", "dark"))
            self._decimals_combo.set(settings.get("weight_decimals", "3"))
        except Exception as e:
            logger.warning(f"Could not load settings: {e}")
    
    def _on_save(self):
        try:
            settings = {
                "company_name": self._company_name.get(),
                "company_phone": self._company_phone.get(),
                "company_address": self._company_address.get(),
                "company_gst": self._company_gst.get(),
                "database_location": self._db_path.get(),
                "backup_folder": self._backup_path.get(),
                "theme": self._theme_combo.get(),
                "weight_decimals": self._decimals_combo.get(),
            }
            self._settings_repo.save_all(settings)
            
            # Apply theme change
            ctk.set_appearance_mode(self._theme_combo.get())
            
            Toast.show(self._app, "Settings saved successfully!", "success")
        except Exception as e:
            Toast.show(self._app, f"Error saving settings: {e}", "error")
    
    def _on_reset(self):
        from config.app_config import DEFAULT_SETTINGS
        try:
            self._settings_repo.save_all(DEFAULT_SETTINGS)
            # Clear and reload
            for entry in [self._company_name, self._company_phone, self._company_address,
                           self._company_gst, self._db_path, self._backup_path]:
                entry.delete(0, "end")
            self._load_settings()
            Toast.show(self._app, "Settings reset to defaults", "info")
        except Exception as e:
            Toast.show(self._app, f"Error: {e}", "error")
