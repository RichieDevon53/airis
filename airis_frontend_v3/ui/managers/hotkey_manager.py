"""
Global hotkey management for the Airis application.
Handles setting up and managing global keyboard shortcuts.
"""
from pynput import keyboard

class HotkeyManager:
    """Manages global hotkeys for the application."""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.hotkey_listener = None
        
    def setup_hotkey_listener(self):
        """Sets up the global hotkey listener for Ctrl+Alt+Space."""
        def on_hotkey():
            if not self.app.is_processing:
                self.app.toggle_window()
            else:
                if self.app.tray_manager.tray_icon:
                    self.app.tray_manager.tray_icon.notify(
                        "Airis is busy processing. Please wait.", 
                        "Airis"
                    )
                
        try:
            self.hotkey_listener = keyboard.GlobalHotKeys({
                '<ctrl>+<alt>+<space>': on_hotkey
            })
            self.hotkey_listener.start()
        except Exception as e:
            print(f"Could not setup global hotkey: {e}")
            if self.app.tray_manager.tray_icon:
                self.app.tray_manager.tray_icon.notify(
                    f"Failed to set hotkey: {e}", 
                    "Airis Error"
                )
                
    def stop_hotkey_listener(self):
        """Stops the global hotkey listener."""
        if self.hotkey_listener:
            self.hotkey_listener.stop()
