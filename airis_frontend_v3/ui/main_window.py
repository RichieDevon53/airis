"""
Main window and application class for Airis.
Coordinates all UI components, managers, and application logic.
"""
import tkinter as tk
import queue
import threading
import sys
import time

from .config.constants import UIConstants
from .managers.style_manager import StyleManager
from .components.widget_factory import WidgetFactory
from .managers.window_manager import WindowManager
from .managers.processing_manager import ProcessingManager
from .managers.tray_manager import TrayManager
from .managers.hotkey_manager import HotkeyManager
from .components.blinking_eye import BlinkingEyeWindow
from .managers.history_manager import HistoryManager
# from .history_window import HistoryWindow
# from app.controllers.maincontroller import controller

class GlassEffectTrayApp:
    """
    Main application class for Airis.
    Manages the Tkinter GUI, system tray icon, global hotkeys,
    and handles communication with AI processing components.
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        # Core components
        self.command_queue = queue.Queue()
        self.running = True
        
        # State flags
        self.is_window_visible = False
        self.is_placeholder = True
        self.is_processing = False

        # Managers
        self.style_manager = StyleManager(self.root)
        self.window_manager = WindowManager(self)
        self.processing_manager = ProcessingManager(self)
        self.tray_manager = TrayManager(self)
        self.hotkey_manager = HotkeyManager(self)
        self.history_manager = HistoryManager(self)
        self.history_window = None
        
        # UI components
        self.blinking_eye = BlinkingEyeWindow(self)
        self.colors = UIConstants.COLORS
        self.fonts = UIConstants.get_platform_font(self.root)
        
        self.setup_ui()
        self.bind_events()
        
        self.tray_manager.setup_tray()
        self.hotkey_manager.setup_hotkey_listener()

        self.process_commands()
        self.root.after(1000, self.show_startup_notification)

    def setup_ui(self):
        """Initializes and configures all UI elements."""
        self.style_manager.setup_window_styling()
        
        # Create widgets using the factory
        self.widget_factory = WidgetFactory(self)
        self.text_input, self.drawing_button, self.voice_button = self.widget_factory.create_content_frame(self.root)
        
        # Set initial state
        self.set_placeholder()
        self.update_drawing_button_state()
        
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.command_queue.put("hide"))

    def process_commands(self):
        """Processes commands from the queue for thread-safe UI updates."""
        try:
            while True:
                command = self.command_queue.get_nowait()
                if callable(command):
                    command()
                elif command == "show":
                    self.window_manager.show_window_internal()
                elif command == "hide":
                    self.window_manager.hide_window_internal()
                elif command == "quit":
                    self.quit_app_internal()
                elif command == "show_processing":
                    self.processing_manager.show_processing_animation()
                elif command == "hide_processing":
                    self.processing_manager.hide_processing_animation()
                elif command == "show_result":
                    self.processing_manager.show_result_window()
                self.command_queue.task_done()
        except queue.Empty:
            pass
        except Exception as e:
            raise e
            print(f"Error processing command: {e}")
        
        if self.running:
            self.root.after(100, self.process_commands)

    def bind_events(self):
        """Binds keyboard and focus events."""
        self.text_input.bind('<FocusIn>', self.clear_placeholder)
        self.text_input.bind('<FocusOut>', self.restore_placeholder)
        self.root.bind('<Escape>', lambda e: self.command_queue.put("hide"))
        self.root.bind('<Return>', self.handle_enter)
        self.text_input.bind('<KeyRelease>', self.update_drawing_button_state)
        
        # Add history shortcut (Ctrl+H)
        self.root.bind('<Control-h>', lambda e: self.show_history())
        self.root.bind('<Control-H>', lambda e: self.show_history())

    def show_history(self):
        """Shows the history window."""
        if self.history_window is None or not self.history_window.window.winfo_exists():
            pass
            # self.history_window = HistoryWindow(self)
        else:
            self.history_window.show()

    def handle_enter(self, event=None, drawing_mode=False):
        """Handles the Enter key press."""
        input_text = self.text_input.get().strip()
        
        print(input_text)
        self.text_input.delete(0, tk.END)
        self.restore_placeholder()
        self.window_manager.hide_window_internal()

        threading.Thread(target=self._process_text_input, args=(input_text,drawing_mode), daemon=True).start()
    
    def _process_text_input(self, text_input, drawing_mode):
        """Internal method to process text input in a separate thread."""
        self.is_processing = True
        self.command_queue.put("show_processing")
        time.sleep(0.3)
        
        start_time = time.time()
        entry_id = None
        
        try:
            # Add initial entry to history
            entry_id = self.history_manager.add_entry(
                query=text_input,
                response="Processing...",
                query_type="text",
                status="processing"
            )
            
            # Execute the input processing
            result = self.processing_manager.execute_input(text_input, drawing_mode)
            
            # Update history with result
            duration = time.time() - start_time
            if entry_id:
                self.history_manager.update_entry(
                    entry_id,
                    response=str(result) if result else "Completed successfully",
                    status="completed",
                    duration=duration
                )
                
        except Exception as e:
            error_msg = f"Error processing text: {e}"
            duration = time.time() - start_time
            
            # Update history with error
            if entry_id:
                self.history_manager.update_entry(
                    entry_id,
                    response=error_msg,
                    status="error",
                    duration=duration
                )
            
            self.command_queue.put(lambda: self.processing_manager.update_response_text(error_msg, is_error=True))
        finally:
            self.is_processing = False
            self.command_queue.put("hide_processing")
            self.command_queue.put("show_result")

    def update_drawing_button_state(self, event=None):
        input_text = self.text_input.get().strip()
        if input_text and not self.is_placeholder:
            self.widget_factory.update_drawing_button_state(tk.NORMAL)
        else:
            self.widget_factory.update_drawing_button_state(tk.DISABLED)

    def log_screenshot_to_history(self, result, error=None):
        """Logs screenshot processing to history."""
        if error:
            self.history_manager.add_entry(
                query="Screenshot analysis",
                response=f"Error: {error}",
                query_type="screenshot",
                status="error"
            )
        else:
            self.history_manager.add_entry(
                query="Screenshot analysis",
                response=str(result) if result else "Screenshot processed successfully",
                query_type="screenshot",
                status="completed"
            )

    def set_placeholder(self, event=None):
        """Sets the placeholder text."""
        self.text_input.delete(0, tk.END)
        self.text_input.insert(0, UIConstants.PLACEHOLDER_TEXT)
        self.text_input.configure(fg=self.colors['text_muted'])
        self.is_placeholder = True

    def clear_placeholder(self, event=None):
        """Clears the placeholder text."""
        if self.is_placeholder:
            self.text_input.delete(0, tk.END)
            self.text_input.configure(fg=self.colors['text_primary'])
            self.is_placeholder = False

    def restore_placeholder(self, event=None):
        """Restores the placeholder if the input is empty."""
        if not self.text_input.get().strip():
            self.set_placeholder()

    def toggle_window(self):
        """Toggles window visibility via the command queue."""
        if self.is_processing:
            return
        if self.is_window_visible:
            self.command_queue.put("hide")
        else:
            self.command_queue.put("show")

    def show_settings(self):
        """Shows the settings view."""
        self.command_queue.put(lambda: self.processing_manager.show_settings_internal())

    def show_startup_notification(self):
        """Shows a startup notification via the tray manager."""
        if self.tray_manager.tray_icon:
            self.tray_manager.show_notification(
                "Airis is running. Press Ctrl+Alt+Space to open.",
                "Airis Ready!"
            )

    def quit_app(self):
        """Queues the application quit command."""
        self.command_queue.put("quit")

    def quit_app_internal(self):
        """Performs cleanup and exits the application."""
        self.running = False
        self.hotkey_manager.stop_hotkey_listener()
        self.tray_manager.stop()
        if self.blinking_eye and self.blinking_eye.window:
            self.blinking_eye.window.destroy()
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

    def run(self):
        """Starts the Tkinter main event loop."""
        self.root.mainloop()
