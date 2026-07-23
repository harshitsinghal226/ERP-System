"""
Print service — Print preview and system print integration.
"""

import os
import sys
import logging
import subprocess
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)


class PrintService:
    """Handles print preview and printing via the OS default PDF viewer."""
    
    @staticmethod
    def print_preview(pdf_path: str) -> bool:
        """
        Open a PDF file in the default viewer for print preview.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if the file was opened successfully
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return False
        
        try:
            if sys.platform == "win32":
                os.startfile(pdf_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", pdf_path])
            else:
                subprocess.Popen(["xdg-open", pdf_path])
            
            logger.info(f"Opened PDF for preview: {pdf_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to open PDF: {e}")
            return False
    
    @staticmethod
    def print_file(pdf_path: str) -> bool:
        """
        Send a PDF directly to the default printer.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if print command was sent
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return False
        
        try:
            if sys.platform == "win32":
                # Use Windows ShellExecute with "print" verb
                import ctypes
                result = ctypes.windll.shell32.ShellExecuteW(
                    None, "print", pdf_path, None, None, 0
                )
                success = result > 32
                if success:
                    logger.info(f"Sent to printer: {pdf_path}")
                return success
            else:
                subprocess.Popen(["lpr", pdf_path])
                return True
        except Exception as e:
            logger.error(f"Failed to print: {e}")
            return False
    
    @staticmethod
    def share_file(pdf_path: str) -> Optional[str]:
        """
        Open the file location for easy sharing.
        
        Returns:
            The directory containing the file
        """
        if not os.path.exists(pdf_path):
            return None
        
        directory = os.path.dirname(pdf_path)
        
        try:
            if sys.platform == "win32":
                # Open Windows Explorer with file selected
                subprocess.Popen(f'explorer /select,"{pdf_path}"')
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", pdf_path])
            else:
                subprocess.Popen(["xdg-open", directory])
            
            return directory
        except Exception as e:
            logger.error(f"Failed to open file location: {e}")
            return directory
