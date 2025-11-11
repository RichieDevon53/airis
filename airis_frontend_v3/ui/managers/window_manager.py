"""
Window manager for the Airis application.
Handles window visibility, positioning, and focus management with slide-fade animations.
"""
import tkinter as tk
from ..config.constants import UIConstants

class WindowManager:
    """Manages the main application window's state and behavior."""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.root = app_instance.root
        self.focus_check_job = None
        self.is_animating = False
        self._cached_geometry = None
        self._final_position = None
        self.alpha_step = 0.06
        self.slide_step = 0.08

    def show_window_internal(self):
        """Shows the main application window with the selected animation."""
        if self.is_animating or self.app.is_window_visible:
            return

        self.is_animating = True
        self.app.is_window_visible = True

        # Center window ONCE and store final position
        self.app.style_manager.center_window()
        self._final_position = self._get_window_position()
        
        # Cache the geometry to prevent repositioning during animation
        self._cached_geometry = self.root.geometry()

        # Prepare window for animation
        self.root.attributes('-alpha', 0)
        self._position_for_slide_start()
        
        
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        
        self._animate_slide_fade_show(0, 0)
        
    def _get_window_position(self):
        """Get the current window position as (x, y) tuple."""
        geometry = self.root.geometry()
        # Parse geometry string like "300x200+100+150"
        parts = geometry.split('+')
        if len(parts) >= 3:
            x = int(parts[1])
            y = int(parts[2])
            return (x, y)
        return None

    def _position_for_slide_start(self):
        """Position window slightly below final position for subtle slide animation."""
        if self._final_position:
            final_x, final_y = self._final_position
            # Start position: same x, but slightly below final position (subtle slide)
            slide_offset = 30  # Small offset for subtle effect
            start_y = final_y + slide_offset
            self.root.geometry(f"{self.root.winfo_reqwidth()}x{self.root.winfo_reqheight()}+{final_x}+{start_y}")

    def _animate_slide_fade_show(self, current_alpha, slide_progress):
        """Combined slide and fade animation for showing the window with subtle upward motion."""
        target_alpha = UIConstants.BLUR_ALPHA
        
        # Calculate new alpha
        new_alpha = min(current_alpha + self.alpha_step, target_alpha)
        self.root.attributes('-alpha', new_alpha)
        
        # Calculate new position for subtle slide
        new_slide_progress = min(slide_progress + self.slide_step, 1.0)
        
        if self._final_position:
            final_x, final_y = self._final_position
            slide_offset = 30  # Small offset for subtle effect
            start_y = final_y + slide_offset
            
            # Smooth easing with sine function for natural motion
            import math
            eased_progress = math.sin(new_slide_progress * math.pi / 2)  # Sine ease-out
            current_y = int(start_y + (final_y - start_y) * eased_progress)
            
            self.root.geometry(f"{self.root.winfo_reqwidth()}x{self.root.winfo_reqheight()}+{final_x}+{current_y}")

        # Continue animation if not complete
        if new_alpha < target_alpha or new_slide_progress < 1.0:
            self.root.after(8, lambda: self._animate_slide_fade_show(new_alpha, new_slide_progress))  # 60fps
        else:
            self.is_animating = False
            self._cached_geometry = None  # Clear cache
            # Animation finished, do final setup
            self.root.after(10, self.auto_focus_text_input)
            self.start_focus_monitoring()

    def _animate_show(self, current_alpha):
        """Original fade-in animation (unchanged)."""
        target_alpha = UIConstants.BLUR_ALPHA
        step = 0.1

        new_alpha = min(current_alpha + step, target_alpha)
        self.root.attributes('-alpha', new_alpha)

        # Ensure geometry doesn't change during animation
        if self._cached_geometry:
            current_geometry = self.root.geometry()
            if current_geometry != self._cached_geometry:
                self.root.geometry(self._cached_geometry)

        if new_alpha < target_alpha:
            self.root.after(15, lambda: self._animate_show(new_alpha))
        else:
            self.is_animating = False
            self._cached_geometry = None  # Clear cache
            # Animation finished, do final setup
            self.root.after(10, self.auto_focus_text_input)
            self.start_focus_monitoring()

    def hide_window_internal(self):
        """Hides the main application window with the selected animation."""
        
        if self.is_animating or not self.app.is_window_visible:
            return

        self.is_animating = True

        # Cache geometry before hiding to prevent positioning issues
        self._cached_geometry = self.root.geometry()
        self._final_position = self._get_window_position()

        # Cancel focus monitoring before hiding
        if self.focus_check_job:
            try:
                self.root.after_cancel(self.focus_check_job)
                self.focus_check_job = None
            except tk.TclError:
                pass
        
        try:
            self.root.unbind('<Button-1>')
        except tk.TclError:
            pass

        current_alpha = self.root.attributes('-alpha')
        
        self._animate_slide_fade_hide(current_alpha, 0)

    def _animate_slide_fade_hide(self, current_alpha, slide_progress):
        """Combined slide and fade animation for hiding the window with subtle downward motion."""
        
        # Calculate new alpha
        new_alpha = max(current_alpha - self.alpha_step, 0.0)
        self.root.attributes('-alpha', new_alpha)
        
        # Calculate new position for subtle slide
        new_slide_progress = min(slide_progress + self.slide_step, 1.0)
        
        if self._final_position:
            final_x, final_y = self._final_position
            slide_offset = 20  # Slightly smaller offset for hide animation
            end_y = final_y + slide_offset
            
            # Smooth easing with sine function for natural motion
            import math
            eased_progress = 1 - math.cos(new_slide_progress * math.pi / 2)  # Sine ease-in
            current_y = int(final_y + (end_y - final_y) * eased_progress)
            
            self.root.geometry(f"{self.root.winfo_reqwidth()}x{self.root.winfo_reqheight()}+{final_x}+{current_y}")

        # Continue animation if not complete
        if new_alpha > 0 or new_slide_progress < 1.0:
            self.root.after(8, lambda: self._animate_slide_fade_hide(new_alpha, new_slide_progress))  # 60fps
        else:
            self.root.withdraw()
            self.app.is_window_visible = False
            self.is_animating = False
            self._cached_geometry = None  # Clear cache

    def _animate_hide(self, current_alpha):
        """Original fade-out animation (unchanged)."""
        step = 0.1
        new_alpha = max(current_alpha - step, 0.0)
        self.root.attributes('-alpha', new_alpha)

        # Maintain position during hide animation
        if self._cached_geometry:
            current_geometry = self.root.geometry()
            if current_geometry != self._cached_geometry:
                self.root.geometry(self._cached_geometry)

        if new_alpha > 0:
            self.root.after(15, lambda: self._animate_hide(new_alpha))
        else:
            self.root.withdraw()
            self.app.is_window_visible = False
            self.is_animating = False
            self._cached_geometry = None  # Clear cache

    def auto_focus_text_input(self):
        """Automatically focuses the text input field."""
        try:
            # First, ensure the window is properly shown and focused
            self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.focus_force()
            
            # Process any pending events
            self.root.update_idletasks()
            
            # Clear placeholder if it exists
            if self.app.is_placeholder:
                self.app.clear_placeholder()
            
            # Focus the text input with multiple attempts
            self.app.text_input.focus_set()
            self.app.text_input.focus_force()
            self.app.text_input.icursor(tk.END)
            
            # Process events again to ensure focus is applied
            self.root.update_idletasks()
            
            # Schedule a delayed focus attempt to ensure it sticks
            self.root.after(100, self._delayed_focus_attempt)
            
        except Exception as e:
            print(f"Error auto-focusing: {e}")
            
    def _delayed_focus_attempt(self):
        """Delayed focus attempt to ensure the text input gets focus."""
        try:
            # Remove topmost after focusing to avoid interfering with other apps
            self.root.attributes('-topmost', False)
            
            # Final focus attempt
            self.app.text_input.focus_set()
            self.app.text_input.focus_force()
            
            # Ensure cursor is at the end
            self.app.text_input.icursor(tk.END)
            
            # Update to apply all changes
            self.root.update_idletasks()
            
        except Exception as e:
            print(f"Error in delayed focus: {e}")


    def start_focus_monitoring(self):
        """Starts the periodic check for focus loss."""
        if self.app.is_processing:
            return
        self.root.bind('<Button-1>', lambda e: None, add='+')
        self.check_window_focus()

    def check_window_focus(self):
        """Recursively checks if the window has focus."""
        if not self.app.is_window_visible or self.app.is_processing or self.is_animating:
            return
            
        try:
            current_focus_widget = self.root.focus_get()
            if current_focus_widget is None or str(current_focus_widget).find(str(self.root)) == -1:
                self.root.after(150, self.confirm_focus_loss)
                return
            self.focus_check_job = self.root.after(100, self.check_window_focus)
        except (tk.TclError, Exception) as e:
            self.focus_check_job = None
            print(f"Error during focus check: {e}")

    def confirm_focus_loss(self):
        """Confirms focus loss before hiding the window."""
        if not self.app.is_window_visible or self.app.is_processing or self.is_animating:
            return
            
        try:
            focused_widget = self.root.focus_get()
            if focused_widget is None or str(focused_widget).find(str(self.root)) == -1:
                x, y = self.root.winfo_pointerxy()
                wx, wy = self.root.winfo_rootx(), self.root.winfo_rooty()
                ww, wh = self.root.winfo_width(), self.root.winfo_height()
                
                if not (wx <= x <= wx + ww and wy <= y <= wy + wh):
                    self.app.command_queue.put("hide")
                    return
            self.focus_check_job = self.root.after(100, self.check_window_focus)
        except (tk.TclError, Exception) as e:
            self.focus_check_job = None
            print(f"Error during confirm focus loss: {e}")
        

