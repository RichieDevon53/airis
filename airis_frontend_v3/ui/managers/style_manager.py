"""
UI styling manager for the Airis application.
Handles theming and widget styling.
"""
from tkinter import ttk
from ..config.constants import UIConstants

class StyleManager:
    """Manages styling for the application."""
    
    def __init__(self, root):
        self.root = root
        self.colors = UIConstants.COLORS
        self.style = ttk.Style()
        
    def setup_window_styling(self):
        """Configures the main window with glassmorphism properties."""
        self.root.title("Airis")
        self.root.attributes('-alpha', UIConstants.BLUR_ALPHA)
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.resizable(False, False)
        # Set initial geometry to prevent showing in top-left
        # self.root.geometry(f"{UIConstants.WINDOW_WIDTH}x{UIConstants.WINDOW_HEIGHT}+0+0")
        
    def center_window(self):
        """Centers the main application window on the screen."""
        # Force geometry update first
        self.root.update_idletasks()
        
        # Get actual window dimensions after widgets are created
        window_width = self.root.winfo_reqwidth() or UIConstants.WINDOW_WIDTH
        window_height = self.root.winfo_reqheight() or UIConstants.WINDOW_HEIGHT
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        
        # Set both size and position explicitly
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Force another update to ensure positioning takes effect
        self.root.update_idletasks()
