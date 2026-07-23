import customtkinter as ctk
from typing import List

class SearchableComboBox(ctk.CTkFrame):
    """
    A true AutoComplete ComboBox that filters options dynamically
    without stealing keyboard focus from the text input.
    """
    def __init__(self, master, values: List[str] = None, font=None, height=36, **kwargs):
        super().__init__(master, fg_color="transparent")
        self._all_values = values or []
        self._font = font or ctk.CTkFont(size=14)
        
        # Core entry widget
        self._entry = ctk.CTkEntry(self, font=self._font, height=height, **kwargs)
        self._entry.pack(fill="both", expand=True)
        
        # State
        self._dropdown = None
        self._dropdown_frame = None
        self._buttons = []
        self._highlighted_index = -1
        self._filtered_values = []
        self._focus_out_timer = None
        
        # Event bindings
        self._entry.bind("<KeyRelease>", self._on_keyrelease)
        self._entry.bind("<Down>", self._on_down)
        self._entry.bind("<Up>", self._on_up)
        # Use a class-level or very early binding for Return to ensure we can stop propagation
        self._entry.bind("<Return>", self._on_return)
        self._entry.bind("<Escape>", self._close_dropdown)
        self._entry.bind("<FocusOut>", self._on_focus_out)
        self._entry.bind("<FocusIn>", self._on_focus_in)
        self._entry.bind("<ButtonRelease-1>", self._on_click)

    def set_all_values(self, values: List[str]):
        """Update the master list of all values."""
        self._all_values = values

    def set(self, value: str):
        """Set the text in the entry."""
        self._entry.delete(0, "end")
        self._entry.insert(0, value)

    def get(self) -> str:
        """Get the text from the entry."""
        return self._entry.get()
        
    def _on_keyrelease(self, event):
        # Ignore navigation and action keys
        if event.keysym in ("Down", "Up", "Return", "Escape", "Tab"):
            return
            
        current_text = self.get().lower()
        if not current_text:
            self._filtered_values = self._all_values
        else:
            self._filtered_values = [v for v in self._all_values if current_text in v.lower()]
            
        self._show_dropdown()
        
    def _show_dropdown(self):
        if not self._filtered_values:
            self._close_dropdown()
            return
            
        if self._dropdown is None or not self._dropdown.winfo_exists():
            # Create a frameless toplevel for the popup
            self._dropdown = ctk.CTkToplevel(self)
            self._dropdown.overrideredirect(True)
            self._dropdown.transient(self.winfo_toplevel())
            self._dropdown.attributes("-topmost", True)
            
            # Position it right below the entry
            x = self._entry.winfo_rootx()
            y = self._entry.winfo_rooty() + self._entry.winfo_height()
            w = self._entry.winfo_width()
            h = min(len(self._filtered_values) * 32 + 10, 200)
            
            self._dropdown.geometry(f"{w}x{h}+{x}+{y}")
            
            self._dropdown_frame = ctk.CTkScrollableFrame(
                self._dropdown, 
                fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"],
                border_width=1,
                border_color=ctk.ThemeManager.theme["CTkFrame"]["border_color"],
                corner_radius=4
            )
            self._dropdown_frame.pack(fill="both", expand=True)
        else:
            # Clear old buttons
            for btn in self._buttons:
                btn.destroy()
            self._buttons.clear()
            
            # Update position/size
            x = self._entry.winfo_rootx()
            y = self._entry.winfo_rooty() + self._entry.winfo_height()
            w = self._entry.winfo_width()
            h = min(len(self._filtered_values) * 32 + 10, 200)
            self._dropdown.geometry(f"{w}x{h}+{x}+{y}")
            
        self._highlighted_index = -1
        self._buttons = []
        
        for i, val in enumerate(self._filtered_values):
            btn = ctk.CTkButton(
                self._dropdown_frame,
                text=val,
                font=self._font,
                fg_color="transparent",
                text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"],
                anchor="w",
                height=30,
                corner_radius=4,
                command=lambda v=val: self._select_value(v)
            )
            btn.pack(fill="x", padx=2, pady=1)
            
            # Bind hover events
            btn.bind("<Enter>", lambda e, idx=i: self._highlight_index(idx))
            self._buttons.append(btn)
            
    def _close_dropdown(self, event=None):
        if self._dropdown and self._dropdown.winfo_exists():
            self._dropdown.destroy()
        self._dropdown = None
        self._buttons = []
        self._highlighted_index = -1
        
    def _on_focus_out(self, event):
        # Delay closing so mouse clicks on dropdown items can process
        if self._focus_out_timer:
            self.after_cancel(self._focus_out_timer)
        self._focus_out_timer = self.after(150, self._close_dropdown)
        
    def _on_focus_in(self, event):
        if self._focus_out_timer:
            self.after_cancel(self._focus_out_timer)
            self._focus_out_timer = None
            
    def _select_value(self, value):
        self.set(value)
        self._close_dropdown()
        self._entry.focus_set()
        self._entry.icursor("end")
        
    def _on_down(self, event):
        if not self._dropdown or not self._dropdown.winfo_exists():
            self._on_keyrelease(event) # Open if closed
            return "break"
            
        if self._buttons:
            new_idx = min(self._highlighted_index + 1, len(self._buttons) - 1)
            self._highlight_index(new_idx)
            return "break"
            
    def _on_up(self, event):
        if not self._dropdown or not self._dropdown.winfo_exists():
            return
            
        if self._buttons:
            new_idx = max(self._highlighted_index - 1, 0)
            self._highlight_index(new_idx)
            return "break"
            
    def _highlight_index(self, index):
        if 0 <= self._highlighted_index < len(self._buttons):
            self._buttons[self._highlighted_index].configure(fg_color="transparent")
            
        self._highlighted_index = index
        if 0 <= index < len(self._buttons):
            # Theme active color
            active_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
            self._buttons[index].configure(fg_color=active_color)
            
            # Basic scrolling logic: if selected item is far down, _parent_canvas.yview_moveto
            if hasattr(self._dropdown_frame, "_parent_canvas"):
                canvas = self._dropdown_frame._parent_canvas
                fraction = index / len(self._buttons)
                canvas.yview_moveto(max(0.0, fraction - 0.1))
            
    def _on_return(self, event):
        # If dropdown is open and an item is highlighted, select it and stop propagation
        if self._dropdown and self._dropdown.winfo_exists() and self._highlighted_index >= 0:
            val = self._filtered_values[self._highlighted_index]
            self._select_value(val)
            return "break"

    def _on_click(self, event=None):
        """Open the dropdown with all values when clicked."""
        if not self._dropdown or not self._dropdown.winfo_exists():
            current_text = self.get().lower()
            if not current_text:
                self._filtered_values = self._all_values
            else:
                self._filtered_values = [v for v in self._all_values if current_text in v.lower()]
            self._show_dropdown()
