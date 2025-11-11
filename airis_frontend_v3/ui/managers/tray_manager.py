"""
System tray manager for the Airis application.
Handles tray icon creation, menu, and global hotkeys.
"""
import threading
from PIL import Image, ImageDraw
import pystray

class TrayManager:
    """Manages the system tray icon and global hotkeys."""
    
    def __init__(self, app_callback):
        self.app_callback = app_callback
        self.tray_icon = None
        
    def create_tray_icon(self):
        """Creates a modern, stylized AI eye icon for the system tray."""
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Modern gradient-like circle background
        draw.ellipse([2, 2, 62, 62], fill=(45, 55, 72, 255), outline=(99, 179, 237, 255), width=3)
        
        # Stylized AI eye with modern, flat design
        # Sclera (white part of the eye)
        draw.ellipse([14, 18, 50, 46], fill=(226, 232, 240, 255))
        # Iris (blue part)
        draw.ellipse([20, 22, 44, 42], fill=(59, 130, 246, 255))
        # Pupil (dark center)
        draw.ellipse([26, 26, 38, 36], fill=(30, 41, 59, 255))
        # Highlight on pupil for a glossy effect
        draw.ellipse([28, 28, 34, 32], fill=(248, 250, 252, 255))
        
        return image
        
    def setup_tray(self):
        """Sets up the system tray icon in a separate thread."""
        def run_tray():
            image = self.create_tray_icon()
            
            # Define context menu for the tray icon
            menu = pystray.Menu(
                pystray.MenuItem("Show/Hide Window", self.toggle_window),
                pystray.MenuItem("History", self.app_callback.show_history),
                pystray.MenuItem("History-sample", pystray.Menu(
                    pystray.MenuItem("History_1", lambda: None),
                    pystray.MenuItem("History_2", lambda: None), 
                    pystray.MenuItem("History_3", lambda: None)
                )),
                pystray.MenuItem("Settings", self.show_settings),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self.quit_app)
            )
            
            self.tray_icon = pystray.Icon(
                "Airis",
                image,
                "Airis - Ctrl+Alt+Space to toggle",
                menu
            )
            
            # Run tray icon (blocks until stopped)
            self.tray_icon.run()
            
        # Start tray in a separate daemon thread
        tray_thread = threading.Thread(target=run_tray, daemon=True)
        tray_thread.start()
                
    def toggle_window(self, icon=None, item=None):
        """Toggles window visibility via callback."""
        self.app_callback.toggle_window()
        
    def show_settings(self, icon=None, item=None):
        """Shows settings via callback."""
        self.app_callback.show_settings()
        
    def quit_app(self, icon=None, item=None):
        """Quits the application via callback."""
        self.app_callback.quit_app()
        
    def show_notification(self, message, title="Airis"):
        """Shows a system notification."""
        if self.tray_icon:
            self.tray_icon.notify(message, title)
            
    def stop(self):
        """Stops the tray icon and hotkey listener."""
        if self.tray_icon:
            self.tray_icon.stop()
