"""
Aashu Jewellers — Silver Manufacturing Management System
=========================================================
Professional ERP application for managing silver issued to and received from Karigars.

Entry point: Initializes the database, seeds default data, and launches the GUI.

Usage:
    python main.py

Author: Aashu Jewellers
Version: 1.0.0
"""

import sys
import os
import logging

# Ensure the application root is in the Python path
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)


def check_dependencies():
    """Verify all required packages are installed."""
    missing = []
    
    try:
        import customtkinter
    except ImportError:
        missing.append("customtkinter")
    
    try:
        import pyodbc
    except ImportError:
        missing.append("pyodbc")
    
    if missing:
        print(f"\n[ERROR] Missing required packages: {', '.join(missing)}")
        print(f"\nInstall them with:")
        print(f"  pip install {' '.join(missing)}")
        print(f"\nOr install all requirements:")
        print(f"  pip install -r requirements.txt")
        sys.exit(1)


def initialize_database():
    """Create the database file and schema if they don't exist."""
    from config.app_config import DB_PATH, ensure_directories
    from database.schema import create_database_file, initialize_schema
    from database.seed_data import seed_all
    from database.connection import DatabaseConnection
    
    logger = logging.getLogger(__name__)
    
    # Create directories
    ensure_directories()
    
    # Create database file if it doesn't exist
    if not os.path.exists(DB_PATH):
        logger.info(f"Creating new database: {DB_PATH}")
        try:
            create_database_file(DB_PATH)
        except Exception as e:
            logger.error(f"Failed to create database file: {e}")
            print(f"\n[ERROR] Failed to create Access database: {e}")
            print(f"\nPlease ensure:")
            print(f"  1. Microsoft Access Database Engine is installed")
            print(f"  2. Python bitness ({__import__('struct').calcsize('P') * 8}-bit) matches the driver")
            print(f"  3. Or manually create an empty .accdb file at: {DB_PATH}")
            sys.exit(1)
    
    # Initialize schema
    try:
        db = DatabaseConnection()
        initialize_schema(db)
        seed_all(db)
        
        # Test connection
        if db.test_connection():
            logger.info("Database initialized and ready")
        else:
            raise RuntimeError("Connection test failed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        print(f"\n[ERROR] Database initialization failed: {e}")
        print(f"\nCheck the log file in the 'logs' directory for details.")
        sys.exit(1)


def main():
    """Application entry point."""
    # Check dependencies first
    check_dependencies()
    
    # Set up logging
    from utils.logger import setup_logging
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("  Aashu Jewellers — Silver Manufacturing Management System")
    logger.info("  Starting application...")
    logger.info("=" * 60)
    
    # Initialize database
    initialize_database()
    
    # Launch GUI
    try:
        from views.app import MainApplication
        
        app = MainApplication()
        
        logger.info("Application window launched")
        app.mainloop()
        
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)
        
        # Show error dialog
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Application Error",
                f"An unexpected error occurred:\n\n{e}\n\n"
                f"Check the log file for details."
            )
            root.destroy()
        except Exception:
            print(f"\n[FATAL] Error: {e}")
        
        sys.exit(1)
    
    logger.info("Application closed normally")


if __name__ == "__main__":
    main()
