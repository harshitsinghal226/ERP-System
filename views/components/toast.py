"""
Toast notification component — non-blocking success/error/info messages.
"""

import customtkinter as ctk
from utils.theme import Colors, Fonts, Spacing


class Toast(ctk.CTkFrame):
    """
    A toast notification that appears at the top of the window
    and auto-dismisses after a timeout.
    """
    
    TYPES = {
        "success": {"bg": "#059669", "icon": "✓"},
        "error": {"bg": "#dc2626", "icon": "✕"},
        "warning": {"bg": "#d97706", "icon": "⚠"},
        "info": {"bg": "#2563eb", "icon": "ℹ"},
    }
    
    def __init__(self, parent, message: str, toast_type: str = "success",
                 duration: int = 3000):
        config = self.TYPES.get(toast_type, self.TYPES["info"])
        
        super().__init__(
            parent,
            fg_color=config["bg"],
            corner_radius=8,
            height=44,
        )
        
        self._duration = duration
        
        # Layout
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=10)
        
        # Icon
        ctk.CTkLabel(
            inner, text=config["icon"],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white",
        ).pack(side="left", padx=(0, 8))
        
        # Message
        ctk.CTkLabel(
            inner, text=message,
            font=ctk.CTkFont(family=Fonts.FAMILY, size=12),
            text_color="white",
        ).pack(side="left", fill="x", expand=True)
        
        # Close button
        ctk.CTkButton(
            inner, text="✕", width=24, height=24,
            fg_color="transparent", hover_color=config["bg"],
            text_color="white", font=ctk.CTkFont(size=12),
            command=self._dismiss,
        ).pack(side="right")
        
        # Auto-dismiss
        self.after(duration, self._dismiss)
    
    def _dismiss(self):
        """Remove the toast."""
        try:
            self.destroy()
        except Exception:
            pass
    
    @staticmethod
    def show(parent, message: str, toast_type: str = "success", duration: int = 3000):
        """
        Show a toast at the top of the parent widget.
        
        Args:
            parent: Parent widget
            message: Text to display
            toast_type: 'success', 'error', 'warning', or 'info'
            duration: Auto-dismiss time in ms
        """
        toast = Toast(parent, message, toast_type, duration)
        toast.place(relx=0.5, y=10, anchor="n", relwidth=0.4)
        toast.lift()
        return toast
