"""
Confirmation dialog — Modal dialog for delete/destructive action confirmation.
"""

import customtkinter as ctk
from utils.theme import Fonts


class ConfirmationDialog(ctk.CTkToplevel):
    """
    A modal confirmation dialog with Yes/No buttons.
    Used before any destructive operation (delete, overwrite, etc.).
    """
    
    def __init__(self, parent, title: str = "Confirm", 
                 message: str = "Are you sure?",
                 confirm_text: str = "Yes, Delete",
                 cancel_text: str = "Cancel",
                 danger: bool = True):
        super().__init__(parent)
        
        self.result = False
        
        # Window config
        self.title(title)
        self.geometry("420x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 420) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 200) // 2
        self.geometry(f"+{x}+{y}")
        
        # Content
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=24, pady=20)
        
        # Warning icon
        icon_text = "⚠" if danger else "❓"
        ctk.CTkLabel(
            frame, text=icon_text,
            font=ctk.CTkFont(size=36),
        ).pack(pady=(0, 12))
        
        # Message
        ctk.CTkLabel(
            frame, text=message,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=13),
            wraplength=360,
        ).pack(pady=(0, 20))
        
        # Buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        ctk.CTkButton(
            btn_frame, text=cancel_text,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=12),
            width=120, height=36,
            fg_color="transparent",
            text_color=("black", "white"),
            border_width=1,
            command=self._cancel,
        ).pack(side="left", expand=True, padx=4)
        
        confirm_color = "#dc2626" if danger else "#059669"
        ctk.CTkButton(
            btn_frame, text=confirm_text,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=12, weight="bold"),
            width=140, height=36,
            fg_color=confirm_color,
            hover_color="#b91c1c" if danger else "#047857",
            command=self._confirm,
        ).pack(side="right", expand=True, padx=4)
        
        # Keyboard bindings
        self.bind("<Return>", lambda e: self._confirm())
        self.bind("<Escape>", lambda e: self._cancel())
        
        self.wait_window()
    
    def _confirm(self):
        self.result = True
        self.destroy()
    
    def _cancel(self):
        self.result = False
        self.destroy()
    
    @staticmethod
    def ask(parent, title: str = "Confirm Delete",
            message: str = "Are you sure you want to delete this record?",
            **kwargs) -> bool:
        """
        Show confirmation dialog and return True if confirmed.
        
        Usage:
            if ConfirmationDialog.ask(self, "Delete?", "This cannot be undone."):
                do_delete()
        """
        dialog = ConfirmationDialog(parent, title, message, **kwargs)
        return dialog.result
