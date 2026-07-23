"""
Thread-safe database connection manager for Microsoft Access.
Provides context manager support and connection pooling.
"""

import threading
import logging
import pyodbc

from config.database_config import get_connection_string

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Manages connections to the Microsoft Access database.
    
    Provides thread-local connections to avoid sharing connections
    across threads. Supports context manager protocol for safe
    resource cleanup.
    
    Usage:
        db = DatabaseConnection()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Karigars")
            rows = cursor.fetchall()
    """
    
    _instance = None
    _lock = threading.Lock()
    _local = threading.local()
    
    def __new__(cls, db_path: str = None):
        """Singleton pattern — one manager per application."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, db_path: str = None):
        if self._initialized:
            return
        self._db_path = db_path
        self._conn_string = None
        self._initialized = True
        logger.info("DatabaseConnection manager initialized")
    
    @property
    def connection_string(self) -> str:
        """Lazy-build the connection string."""
        if self._conn_string is None:
            self._conn_string = get_connection_string(self._db_path)
        return self._conn_string
    
    def get_connection(self) -> 'ConnectionContext':
        """
        Get a context manager that provides a database connection.
        
        Returns:
            ConnectionContext that yields a pyodbc.Connection
        """
        return ConnectionContext(self.connection_string)
    
    def execute_query(self, query: str, params: tuple = None) -> list:
        """
        Execute a SELECT query and return all rows.
        
        Args:
            query: SQL SELECT statement with ? placeholders
            params: Tuple of parameter values
            
        Returns:
            List of pyodbc.Row objects
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            # Convert to list of dicts for easier consumption
            return [dict(zip(columns, row)) for row in rows]
    
    def execute_non_query(self, query: str, params: tuple = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL statement with ? placeholders
            params: Tuple of parameter values
            
        Returns:
            Number of rows affected, or last inserted ID for INSERT
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Try to get the auto-generated ID for INSERT statements
            row_count = cursor.rowcount
            
            if query.strip().upper().startswith("INSERT"):
                cursor.execute("SELECT @@IDENTITY")
                result = cursor.fetchone()
                last_id = result[0] if result and result[0] else row_count
                conn.commit()
                return last_id
            
            conn.commit()
            return row_count
    
    def execute_many(self, query: str, params_list: list) -> int:
        """
        Execute a query with multiple parameter sets (batch operation).
        
        Args:
            query: SQL statement with ? placeholders
            params_list: List of parameter tuples
            
        Returns:
            Total rows affected
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            total = 0
            for params in params_list:
                cursor.execute(query, params)
                total += cursor.rowcount
            conn.commit()
            return total
    
    def test_connection(self) -> bool:
        """Test if the database connection works."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                logger.info("Database connection test: SUCCESS")
                return True
        except Exception as e:
            logger.error(f"Database connection test: FAILED — {e}")
            return False
    
    @classmethod
    def reset(cls):
        """Reset the singleton instance (used for testing or re-initialization)."""
        with cls._lock:
            cls._instance = None


class ConnectionContext:
    """
    Context manager for database connections.
    Ensures connections are properly closed after use.
    """
    
    def __init__(self, conn_string: str):
        self._conn_string = conn_string
        self._connection = None
    
    def __enter__(self) -> pyodbc.Connection:
        try:
            self._connection = pyodbc.connect(self._conn_string)
            return self._connection
        except pyodbc.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection:
            try:
                if exc_type:
                    self._connection.rollback()
                self._connection.close()
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
        return False  # Don't suppress exceptions
