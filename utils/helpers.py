"""
Utility helper functions used across the application.
"""

from datetime import datetime, date
from typing import Optional

from config.app_config import DATE_FORMAT, DATE_DB_FORMAT, DATETIME_FORMAT


# ── Date Helpers ───────────────────────────────────────────────────────

def format_date(dt: datetime, fmt: str = DATE_FORMAT) -> str:
    """Format a datetime to display string (DD-MM-YYYY)."""
    if isinstance(dt, str):
        return dt
    if dt is None:
        return ""
    return dt.strftime(fmt)


def parse_date(date_str: str, fmt: str = DATE_FORMAT) -> Optional[datetime]:
    """Parse a display date string to datetime."""
    if not date_str or not date_str.strip():
        return None
    try:
        return datetime.strptime(date_str.strip(), fmt)
    except ValueError:
        return None


def to_db_date(date_str: str) -> Optional[str]:
    """Convert display date (DD-MM-YYYY) to DB date (YYYY-MM-DD)."""
    dt = parse_date(date_str)
    if dt:
        return dt.strftime(DATE_DB_FORMAT)
    return None


def from_db_date(db_date) -> str:
    """Convert DB date to display format (DD-MM-YYYY)."""
    if isinstance(db_date, datetime):
        return db_date.strftime(DATE_FORMAT)
    if isinstance(db_date, date):
        return db_date.strftime(DATE_FORMAT)
    if isinstance(db_date, str):
        try:
            dt = datetime.strptime(db_date, DATE_DB_FORMAT)
            return dt.strftime(DATE_FORMAT)
        except ValueError:
            return db_date
    return ""


def today_str() -> str:
    """Get today's date as display string."""
    return datetime.now().strftime(DATE_FORMAT)


def today_db_str() -> str:
    """Get today's date as DB string."""
    return datetime.now().strftime(DATE_DB_FORMAT)


def get_current_month() -> int:
    """Get current month number (1-12)."""
    return datetime.now().month


def get_current_year() -> int:
    """Get current year."""
    return datetime.now().year


# ── Number Formatting ──────────────────────────────────────────────────

def format_weight(value: float, decimals: int = 3) -> str:
    """Format weight value with specified decimal places."""
    if value is None:
        return "0.000"
    return f"{float(value):.{decimals}f}"


def format_currency(value: float) -> str:
    """Format currency with Indian number system (₹ prefix)."""
    if value is None:
        return "₹0.00"
    
    # Indian number system: 1,00,000.00
    is_negative = value < 0
    value = abs(value)
    
    integer_part = int(value)
    decimal_part = f"{value - integer_part:.2f}"[1:]  # Get .XX part
    
    # Format integer part in Indian system
    s = str(integer_part)
    if len(s) > 3:
        last_three = s[-3:]
        remaining = s[:-3]
        # Add commas every 2 digits for the remaining part
        formatted = ""
        for i, digit in enumerate(reversed(remaining)):
            if i > 0 and i % 2 == 0:
                formatted = "," + formatted
            formatted = digit + formatted
        result = f"{formatted},{last_three}"
    else:
        result = s
    
    prefix = "-" if is_negative else ""
    return f"{prefix}₹{result}{decimal_part}"


def safe_float(value, default: float = 0.0) -> float:
    """Safely convert a value to float."""
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value, default: int = 0) -> int:
    """Safely convert a value to int."""
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (ValueError, TypeError):
        return default


# ── String Helpers ─────────────────────────────────────────────────────

def truncate(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis if too long."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def title_case(text: str) -> str:
    """Convert text to title case."""
    if not text:
        return ""
    return text.strip().title()


# ── Status Helpers ─────────────────────────────────────────────────────

def get_balance_status(pending: float) -> str:
    """
    Determine balance status based on pending silver.
    
    Args:
        pending: Pending silver amount (Issued - Received)
    
    Returns:
        'Naam' if pending > 0, 'Jama' if pending < 0, 'Settled' if zero
    """
    if pending > 0.001:  # Small epsilon to handle floating point
        return "Naam"
    elif pending < -0.001:
        return "Jama"
    return "Settled"


def calculate_scrap(gross_weight: float, labour_weight: float) -> float:
    """Calculate scrap weight: Gross - Labour."""
    return max(0, gross_weight - labour_weight)


def calculate_net_weight(gross_weight: float, scrap_weight: float) -> float:
    """Calculate net weight: Gross - Scrap."""
    return max(0, gross_weight - scrap_weight)
