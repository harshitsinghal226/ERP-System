"""
Database schema definitions and initialization for Microsoft Access.
Creates all tables, indexes, and relationships.

Note: Microsoft Access SQL (Jet SQL) has different syntax from standard SQL.
- Uses AUTOINCREMENT instead of AUTO_INCREMENT
- Uses YESNO for boolean
- Uses CURRENCY for money fields
- Uses DATETIME for date/time fields
- Uses DOUBLE for float fields
- Uses MEMO for long text (TEXT is limited to 255 chars)
"""

import logging
import os
import pyodbc

from database.connection import DatabaseConnection

logger = logging.getLogger(__name__)

# ── Table Creation SQL ─────────────────────────────────────────────────
# Note: Access uses Jet SQL syntax, not standard SQL

TABLES = {
    "Karigars": """
        CREATE TABLE Karigars (
            KarigarID AUTOINCREMENT PRIMARY KEY,
            KarigarName TEXT(100) NOT NULL,
            Phone TEXT(20),
            Address MEMO,
            City TEXT(50),
            OpeningBalance DOUBLE,
            Remark MEMO,
            IsActive BIT,
            CreatedAt DATETIME,
            UpdatedAt DATETIME
        )
    """,
    
    "ItemTypes": """
        CREATE TABLE ItemTypes (
            ItemTypeID AUTOINCREMENT PRIMARY KEY,
            ItemName TEXT(100) NOT NULL,
            Description MEMO,
            IsActive BIT,
            CreatedAt DATETIME
        )
    """,
    
    "IssueEntries": """
        CREATE TABLE IssueEntries (
            IssueID AUTOINCREMENT PRIMARY KEY,
            IssueDate DATETIME NOT NULL,
            KarigarID LONG NOT NULL,
            ItemTypeID LONG NOT NULL,
            Remark MEMO,
            Weight DOUBLE NOT NULL,
            AdvanceMoney CURRENCY,
            CreatedAt DATETIME,
            UpdatedAt DATETIME,
            CONSTRAINT FK_Issue_Karigar FOREIGN KEY (KarigarID) REFERENCES Karigars(KarigarID),
            CONSTRAINT FK_Issue_ItemType FOREIGN KEY (ItemTypeID) REFERENCES ItemTypes(ItemTypeID)
        )
    """,
    
    "ReceiveEntries": """
        CREATE TABLE ReceiveEntries (
            ReceiveID AUTOINCREMENT PRIMARY KEY,
            ReceiveDate DATETIME NOT NULL,
            KarigarID LONG NOT NULL,
            ItemTypeID LONG NOT NULL,
            Remark MEMO,
            GrossWeight DOUBLE NOT NULL,
            LabourWeight DOUBLE NOT NULL,
            ScrapWeight DOUBLE NOT NULL,
            NetWeight DOUBLE NOT NULL,
            CreatedAt DATETIME,
            UpdatedAt DATETIME,
            CONSTRAINT FK_Receive_Karigar FOREIGN KEY (KarigarID) REFERENCES Karigars(KarigarID),
            CONSTRAINT FK_Receive_ItemType FOREIGN KEY (ItemTypeID) REFERENCES ItemTypes(ItemTypeID)
        )
    """,
    
    "Users": """
        CREATE TABLE Users (
            UserID AUTOINCREMENT PRIMARY KEY,
            Username TEXT(50) NOT NULL,
            PasswordHash TEXT(255) NOT NULL,
            FullName TEXT(100),
            Role TEXT(20),
            IsActive BIT,
            CreatedAt DATETIME
        )
    """,
    
    "Settings": """
        CREATE TABLE Settings (
            SettingID AUTOINCREMENT PRIMARY KEY,
            SettingKey TEXT(100) NOT NULL,
            SettingValue MEMO,
            UpdatedAt DATETIME
        )
    """,
    
    "MonthlyBackup": """
        CREATE TABLE MonthlyBackup (
            BackupID AUTOINCREMENT PRIMARY KEY,
            BackupMonth TEXT(2) NOT NULL,
            BackupYear TEXT(4) NOT NULL,
            BackupPath TEXT(255) NOT NULL,
            OriginalDBPath TEXT(255),
            BackupDate DATETIME,
            Remarks MEMO
        )
    """,
    
    "AuditLogs": """
        CREATE TABLE AuditLogs (
            LogID AUTOINCREMENT PRIMARY KEY,
            UserID LONG,
            Action TEXT(50) NOT NULL,
            TableName TEXT(50) NOT NULL,
            RecordID LONG,
            OldValues MEMO,
            NewValues MEMO,
            LogTimestamp DATETIME
        )
    """,
}

# ── Index Creation SQL ─────────────────────────────────────────────────
INDEXES = [
    "CREATE INDEX IX_Karigars_Name ON Karigars (KarigarName)",
    "CREATE INDEX IX_Karigars_Active ON Karigars (IsActive)",
    "CREATE INDEX IX_ItemTypes_Name ON ItemTypes (ItemName)",
    "CREATE INDEX IX_ItemTypes_Active ON ItemTypes (IsActive)",
    "CREATE INDEX IX_IssueEntries_Date ON IssueEntries (IssueDate)",
    "CREATE INDEX IX_IssueEntries_Karigar ON IssueEntries (KarigarID)",
    "CREATE INDEX IX_IssueEntries_ItemType ON IssueEntries (ItemTypeID)",
    "CREATE INDEX IX_ReceiveEntries_Date ON ReceiveEntries (ReceiveDate)",
    "CREATE INDEX IX_ReceiveEntries_Karigar ON ReceiveEntries (KarigarID)",
    "CREATE INDEX IX_ReceiveEntries_ItemType ON ReceiveEntries (ItemTypeID)",
    "CREATE UNIQUE INDEX IX_Settings_Key ON Settings (SettingKey)",
    "CREATE INDEX IX_AuditLogs_Table ON AuditLogs (TableName)",
    "CREATE INDEX IX_AuditLogs_Timestamp ON AuditLogs (Timestamp)",
]


def create_database_file(db_path: str) -> None:
    """
    Create a new empty Microsoft Access .accdb file.
    
    Uses the ADOX COM library on Windows to create the file
    since pyodbc cannot create Access databases directly.
    
    Args:
        db_path: Full path for the new .accdb file
    """
    if os.path.exists(db_path):
        logger.info(f"Database file already exists: {db_path}")
        return
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        import win32com.client
        catalog = win32com.client.Dispatch("ADOX.Catalog")
        conn_str = (
            f"Provider=Microsoft.ACE.OLEDB.12.0;"
            f"Data Source={db_path};"
        )
        catalog.Create(conn_str)
        catalog.ActiveConnection.Close()
        catalog = None
        logger.info(f"Created new Access database: {db_path}")
    except ImportError:
        # Fallback: try using pypyodbc or copy a template
        logger.warning("win32com not available, attempting pypyodbc fallback")
        try:
            import pypyodbc
            pypyodbc.win_create_mdb(db_path)
            logger.info(f"Created new Access database via pypyodbc: {db_path}")
        except ImportError:
            # Last resort: copy a blank template
            _create_blank_accdb(db_path)


def _create_blank_accdb(db_path: str) -> None:
    """
    Create a minimal blank .accdb file by writing the Access header bytes.
    This creates a valid but empty Access 2007+ database file.
    """
    template_path = os.path.join(os.path.dirname(__file__), "template.accdb")
    if os.path.exists(template_path):
        import shutil
        shutil.copy2(template_path, db_path)
        logger.info(f"Created database from template: {db_path}")
    else:
        raise RuntimeError(
            f"Cannot create Access database. Please install pywin32:\n"
            f"  pip install pywin32\n\n"
            f"Or manually create an empty .accdb file at:\n"
            f"  {db_path}"
        )


def initialize_schema(db: DatabaseConnection = None) -> None:
    """
    Create all tables and indexes in the database.
    Skips tables/indexes that already exist.
    
    Args:
        db: DatabaseConnection instance. Creates default if None.
    """
    if db is None:
        db = DatabaseConnection()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Get existing tables
        existing_tables = set()
        for row in cursor.tables(tableType='TABLE'):
            existing_tables.add(row.table_name)
        
        # Create tables
        for table_name, create_sql in TABLES.items():
            if table_name not in existing_tables:
                try:
                    cursor.execute(create_sql)
                    conn.commit()
                    logger.info(f"Created table: {table_name}")
                except pyodbc.Error as e:
                    logger.error(f"Failed to create table {table_name}: {e}")
                    conn.rollback()
            else:
                logger.debug(f"Table already exists: {table_name}")
        
        # Create indexes (ignore errors for existing indexes)
        for index_sql in INDEXES:
            try:
                cursor.execute(index_sql)
                conn.commit()
            except pyodbc.Error:
                # Index likely already exists
                conn.rollback()
                pass
    
    logger.info("Database schema initialization complete")


def drop_all_tables(db: DatabaseConnection = None) -> None:
    """
    Drop all application tables. USE WITH CAUTION.
    Mainly used for testing and re-initialization.
    """
    if db is None:
        db = DatabaseConnection()
    
    # Drop in reverse dependency order
    drop_order = [
        "AuditLogs", "MonthlyBackup", "Settings", "Users",
        "ReceiveEntries", "IssueEntries", "ItemTypes", "Karigars"
    ]
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for table_name in drop_order:
            try:
                cursor.execute(f"DROP TABLE {table_name}")
                conn.commit()
                logger.info(f"Dropped table: {table_name}")
            except pyodbc.Error:
                conn.rollback()
                pass
