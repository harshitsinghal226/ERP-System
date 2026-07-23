"""
Application configuration constants and paths.
Centralizes all app-wide settings for Aashu Jewellers Silver Manufacturing System.
"""

import os
import sys

def get_app_root() -> str:
    """Get the application root directory, handling both dev and PyInstaller bundled modes."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── Application Metadata ──────────────────────────────────────────────
APP_NAME = "Aashu Jewellers"
APP_TITLE = "Aashu Jewellers — Silver Manufacturing Management System"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Professional Silver Manufacturing ERP for Aashu Jewellers"

# ── Paths ──────────────────────────────────────────────────────────────
APP_ROOT = get_app_root()
DATA_DIR = os.path.join(APP_ROOT, "data")
BACKUP_DIR = os.path.join(APP_ROOT, "backups")
REPORTS_DIR = os.path.join(APP_ROOT, "reports", "generated")
ASSETS_DIR = os.path.join(APP_ROOT, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
LOGS_DIR = os.path.join(APP_ROOT, "logs")

# ── Database ───────────────────────────────────────────────────────────
DB_FILENAME = "aashu_jewellers.accdb"
DB_PATH = os.path.join(DATA_DIR, DB_FILENAME)

# ── Default Settings ──────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    "company_name": "Aashu Jewellers",
    "company_address": "",
    "company_phone": "",
    "company_gst": "",
    "company_logo": "",
    "backup_folder": BACKUP_DIR,
    "database_location": DB_PATH,
    "theme": "light",
    "weight_unit": "grams",
    "weight_decimals": "3",
    "currency": "INR",
    "currency_symbol": "₹",
    "printer_name": "",
    "page_size": "A4",
}

# ── UI Defaults ────────────────────────────────────────────────────────
WINDOW_WIDTH = 1366
WINDOW_HEIGHT = 768
MIN_WINDOW_WIDTH = 1024
MIN_WINDOW_HEIGHT = 768
SIDEBAR_WIDTH = 250
SIDEBAR_COLLAPSED_WIDTH = 64

# ── Formatting ─────────────────────────────────────────────────────────
DATE_FORMAT = "%d-%m-%Y"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"

DATE_DB_FORMAT = "%Y-%m-%d"
DATETIME_DB_FORMAT = "%Y-%m-%d %H:%M:%S"

def ensure_directories():
    """Ensure all required directories exist."""
    directories = [DATA_DIR, BACKUP_DIR, REPORTS_DIR, LOGS_DIR, ASSETS_DIR, ICONS_DIR]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
