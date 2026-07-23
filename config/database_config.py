"""
Database configuration and driver detection for Microsoft Access.
Handles 32-bit vs 64-bit driver detection and DSN-less connection strings.
"""

import struct
import logging

from config.app_config import DB_PATH

logger = logging.getLogger(__name__)

# Known Access ODBC driver names (ordered by preference)
ACCESS_DRIVERS = [
    "Microsoft Access Driver (*.mdb, *.accdb)",
    "Microsoft Access Driver (*.mdb)",
]


def get_python_bitness() -> int:
    """Detect whether Python is running as 32-bit or 64-bit."""
    return struct.calcsize("P") * 8


def detect_access_driver() -> str:
    """
    Detect the installed Microsoft Access ODBC driver.
    
    Returns the driver name string, or raises RuntimeError if none found.
    The driver bitness must match Python's bitness (32 or 64 bit).
    """
    try:
        import pyodbc
        available_drivers = pyodbc.drivers()
        
        for driver in ACCESS_DRIVERS:
            if driver in available_drivers:
                logger.info(f"Found Access ODBC driver: {driver}")
                return driver
        
        # Log available drivers for debugging
        logger.warning(f"No Access driver found. Available drivers: {available_drivers}")
        
        raise RuntimeError(
            f"No Microsoft Access ODBC driver found.\n\n"
            f"Python is {get_python_bitness()}-bit. You need the matching "
            f"{get_python_bitness()}-bit Microsoft Access Database Engine.\n\n"
            f"Download from:\n"
            f"https://www.microsoft.com/en-us/download/details.aspx?id=54920\n\n"
            f"Available ODBC drivers: {available_drivers}"
        )
    except ImportError:
        raise RuntimeError(
            "pyodbc is not installed. Run: pip install pyodbc"
        )


def get_connection_string(db_path: str = None) -> str:
    """
    Build a DSN-less connection string for the Access database.
    
    Args:
        db_path: Optional override path to the .accdb file.
                 Defaults to the configured DB_PATH.
    
    Returns:
        ODBC connection string.
    """
    path = db_path or DB_PATH
    driver = detect_access_driver()
    
    conn_str = (
        f"DRIVER={{{driver}}};"
        f"DBQ={path};"
    )
    
    logger.debug(f"Connection string built for: {path}")
    return conn_str
