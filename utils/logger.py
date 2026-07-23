"""
Logging configuration for Aashu Jewellers application.
Sets up file and console logging with rotation.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

from config.app_config import LOGS_DIR, APP_NAME


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Configure application-wide logging.
    
    Logs to both console and a rotating file.
    
    Args:
        level: Logging level (default: INFO)
        
    Returns:
        Root logger instance
    """
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    log_file = os.path.join(LOGS_DIR, "app.log")
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # File handler with rotation (5 MB per file, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logger = logging.getLogger(APP_NAME)
    logger.info(f"Logging initialized — log file: {log_file}")
    
    return logger
