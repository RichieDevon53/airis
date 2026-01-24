"""
Processing manager for handling AI operations and screenshot processing.
Manages the flow of AI processing tasks and UI updates.
"""
import time
from typing import Union
from app.controllers.maincontroller import controller
from app.utils.screenshot import screenshot

class ProcessingManager:
    """Manages AI processing operations and related UI updates."""
    
    def __init__(self, app_instance):
        self.app = app_instance
        
    def execute_input(self, string: str, drawing_mode: bool):
        """Calls the external controller function to process input."""
        try:
            time.sleep(0.2)
            
            screenshot()
            
            if drawing_mode:
                response_text = controller.glass_board(string)
                valid_output = {
                    "explanation": "Your overlay still can be seen on the history section.",
                    "short_answer": "Drawing Done!"
                }
            else: 
                response_text = controller(string)
                valid_output = response_text
            
            self.app.command_queue.put(
                lambda: self.update_response_text(valid_output)
            )
        except Exception as e:
            error_message = f"An error occurred during processing: {e}"
            self.app.command_queue.put(
                lambda: self.update_response_text(error_message, is_error=True)
            )
            
    def update_response_text(self, text: Union[dict, str], is_error=False):
        """Updates the main response text area."""
        if self.app.tray_manager.tray_icon:
            if is_error:
                self.app.tray_manager.show_notification(
                text[:256],
                "Oops, something went wrong."
            )
            else:
                self.app.tray_manager.show_notification(
                    text["explanation"][:255],
                    text["short_answer"][:64]
                )
            
    def show_processing_animation(self):
        """Shows the blinking eye animation."""
        if self.app.blinking_eye:
            self.app.blinking_eye.show()
    
    def hide_processing_animation(self):
        """Hides the blinking eye animation."""
        if self.app.blinking_eye:
            self.app.blinking_eye.hide()
    
    def show_result_window(self):
        """Shows the main window after processing."""
        self.app.window_manager.show_window_internal()
        self.app.window_manager.auto_focus_text_input()
        
    def show_settings_internal(self):
        """Shows settings window (placeholder)."""
        if not self.app.is_processing:
            self.app.window_manager.show_window_internal()
            self.update_response_text("Settings functionality is under development. Coming soon!")
