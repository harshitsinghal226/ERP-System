"""
Seed data for initial database population.
Pre-populates item types and default settings.
"""

import logging
from datetime import datetime

from database.connection import DatabaseConnection
from config.app_config import DEFAULT_SETTINGS

logger = logging.getLogger(__name__)

# ── Default Item Types ─────────────────────────────────────────────────
DEFAULT_ITEM_TYPES = [
    ("Silver Chain Raw", "Raw silver chain material"),
    ("Anklet Raw", "Raw anklet silver material"),
    ("Ring Raw", "Raw ring silver material"),
    ("Wire", "Silver wire"),
    ("Pipe", "Silver pipe"),
    ("Sheet", "Silver sheet"),
    ("Bangle Raw", "Raw bangle silver material"),
    ("Necklace Raw", "Raw necklace silver material"),
    ("Bracelet Raw", "Raw bracelet silver material"),
    ("Earring Raw", "Raw earring silver material"),
    ("Toe Ring Raw", "Raw toe ring silver material"),
    ("Custom Item", "Custom/other silver item"),
]

# ── Default Admin User ─────────────────────────────────────────────────
DEFAULT_USER = {
    "username": "admin",
    "password_hash": "admin123",  # Will be hashed in future
    "full_name": "Administrator",
    "role": "admin",
}


def seed_item_types(db: DatabaseConnection = None) -> None:
    """Insert default item types if the table is empty."""
    if db is None:
        db = DatabaseConnection()
    
    # Check if item types already exist
    result = db.execute_query("SELECT COUNT(*) AS cnt FROM ItemTypes")
    if result and result[0]["cnt"] > 0:
        logger.debug("Item types already seeded, skipping")
        return
    
    for item_name, description in DEFAULT_ITEM_TYPES:
        db.execute_non_query(
            "INSERT INTO ItemTypes (ItemName, Description, IsActive, CreatedAt) "
            "VALUES (?, ?, -1, NOW())",
            (item_name, description)
        )
    
    logger.info(f"Seeded {len(DEFAULT_ITEM_TYPES)} default item types")


def seed_settings(db: DatabaseConnection = None) -> None:
    """Insert default settings if the table is empty."""
    if db is None:
        db = DatabaseConnection()
    
    result = db.execute_query("SELECT COUNT(*) AS cnt FROM Settings")
    if result and result[0]["cnt"] > 0:
        logger.debug("Settings already seeded, skipping")
        return
    
    for key, value in DEFAULT_SETTINGS.items():
        db.execute_non_query(
            "INSERT INTO Settings (SettingKey, SettingValue, UpdatedAt) "
            "VALUES (?, ?, NOW())",
            (key, str(value))
        )
    
    logger.info(f"Seeded {len(DEFAULT_SETTINGS)} default settings")


def seed_default_user(db: DatabaseConnection = None) -> None:
    """Insert default admin user if no users exist."""
    if db is None:
        db = DatabaseConnection()
    
    result = db.execute_query("SELECT COUNT(*) AS cnt FROM Users")
    if result and result[0]["cnt"] > 0:
        logger.debug("Users already seeded, skipping")
        return
    
    db.execute_non_query(
        "INSERT INTO Users (Username, PasswordHash, FullName, Role, IsActive, CreatedAt) "
        "VALUES (?, ?, ?, ?, -1, NOW())",
        (
            DEFAULT_USER["username"],
            DEFAULT_USER["password_hash"],
            DEFAULT_USER["full_name"],
            DEFAULT_USER["role"],
        )
    )
    
    logger.info("Seeded default admin user")


def seed_all(db: DatabaseConnection = None) -> None:
    """Run all seed operations."""
    if db is None:
        db = DatabaseConnection()
    
    seed_item_types(db)
    seed_settings(db)
    seed_default_user(db)
    logger.info("All seed data populated successfully")
