"""
Application-wide constants for Aashu Jewellers.
"""

# ── Entry Types ────────────────────────────────────────────────────────
ENTRY_TYPE_ISSUE = "I"
ENTRY_TYPE_RECEIVE = "R"

# ── Status Labels ──────────────────────────────────────────────────────
STATUS_NAAM = "Naam"       # Karigar owes silver (Issued > Received)
STATUS_JAMA = "Jama"       # Karigar has credit (Received >= Issued)
STATUS_SETTLED = "Settled"  # Balance is zero

# ── User Roles ─────────────────────────────────────────────────────────
ROLE_ADMIN = "admin"
ROLE_USER = "user"

# ── Navigation Items ───────────────────────────────────────────────────
NAV_DASHBOARD = "dashboard"
NAV_ISSUE = "issue"
NAV_RECEIVE = "receive"
NAV_KARIGAR = "karigar"
NAV_ITEM_TYPE = "item_type"
NAV_SEARCH = "search"
NAV_REPORTS = "reports"
NAV_BACKUP = "backup"
NAV_SETTINGS = "settings"

# ── Keyboard Shortcuts ─────────────────────────────────────────────────
SHORTCUTS = {
    "new": "<Control-n>",
    "save": "<Control-s>",
    "delete": "<Delete>",
    "search": "<Control-f>",
    "print": "<Control-p>",
    "clear": "<Escape>",
    "refresh": "<F5>",
    "home": "<Alt-h>",
    "exit": "<Alt-F4>",
}

# ── Report Types ───────────────────────────────────────────────────────
REPORT_KARIGAR_LEDGER = "karigar_ledger"
REPORT_ALL_KARIGARS = "all_karigars_summary"
REPORT_DATE_WISE = "date_wise"
REPORT_MONTHLY_SUMMARY = "monthly_summary"

# ── Months ─────────────────────────────────────────────────────────────
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
