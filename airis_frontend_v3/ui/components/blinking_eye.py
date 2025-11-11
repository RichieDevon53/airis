import tkinter as tk

class BlinkingEyeWindow:
    """
    A separate, small Toplevel window displaying a blinking eye animation.
    This acts as a visual indicator when the main application is processing.
    """
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.window = None
        self.is_visible = False
        self.animation_running = False
        self.animation_thread = None # Not strictly used as animation is Tkinter's after loop
        self.eye_canvas = None
        self.eye_state = "open"  # "open", "half", "closed"
        self.blink_cycle = 0
        
    def create_window(self):
        """
        Creates the blinking eye animation window as a Toplevel widget.
        Configures it to be topmost, transparent, and without window decorations.
        Positions it in the top-right corner of the screen.
        """
        if self.window:
            return
            
        self.window = tk.Toplevel()
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.9)
        self.window.overrideredirect(True) # Remove window borders and title bar
        self.window.resizable(False, False)
        
        # Make the window background transparent
        try:
            # For Windows
            self.window.wm_attributes('-transparentcolor', 'gray90')
        except:
            try:
                # For macOS
                self.window.wm_attributes('-transparent', True)
            except:
                # Fallback - just use a very low alpha
                self.window.attributes('-alpha', 0.1)
        
        # Position in top-right corner
        window_size = 120
        screen_width = self.window.winfo_screenwidth()
        x = screen_width - window_size - 20 # 20px padding from right edge
        y = 20 # 20px padding from top edge
        
        self.window.geometry(f"{window_size}x{window_size}+{x}+{y}")
        # Set background to the transparent color (gray90 for Windows)
        self.window.configure(bg='gray90')
        
        # Create canvas for eye animation with transparent background
        self.eye_canvas = tk.Canvas(
            self.window,
            width=100,
            height=100,
            bg='gray90',  # Match the transparent color
            highlightthickness=0 # No border around canvas
        )
        self.eye_canvas.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Hide initially
        self.window.withdraw()
        
    def show(self):
        """Shows the blinking eye animation window and starts the animation."""
        if not self.window:
            self.create_window()
            
        self.window.deiconify() # Make window visible
        self.window.lift() # Bring to front
        self.is_visible = True
        self.start_animation()
        
    def hide(self):
        """Hides the blinking eye animation window and stops the animation."""
        if self.window:
            self.window.withdraw() # Hide window
        self.is_visible = False
        self.stop_animation()
        
    def start_animation(self):
        """Starts the blinking animation by scheduling the first frame."""
        if self.animation_running:
            return
            
        self.animation_running = True
        self.animate_eye() # Call the first frame immediately
        
    def stop_animation(self):
        """Stops the blinking animation."""
        self.animation_running = False
        # The 'after' call will automatically stop when animation_running is False
        
    def animate_eye(self):
        """
        Performs one frame of the eye blinking animation.
        Updates the eye state and redraws the eye, then schedules the next frame.
        """
        if not self.animation_running or not self.is_visible:
            return
            
        self.draw_eye()
        
        # Blink cycle: open -> half -> closed -> half -> open
        # More 'open' frames for longer open duration, then quick blink
        blink_states = ["open", "open", "open", "open", "half", "closed", "half", "open"]
        
        self.blink_cycle = (self.blink_cycle + 1) % len(blink_states)
        self.eye_state = blink_states[self.blink_cycle]
        
        # Schedule next frame (about 8 FPS for smooth blinking)
        if self.window and self.animation_running:
            self.window.after(125, self.animate_eye) # 125ms = 8 frames per second
            
    def draw_eye(self):
        """
        Draws the eye on the canvas based on the current `eye_state`.
        Includes logic for open, half-closed, and closed eye representations.
        The background around the eye is now transparent.
        """
        if not self.eye_canvas:
            return
            
        self.eye_canvas.delete("all") # Clear previous drawing
        
        # Eye dimensions (relative to canvas size)
        center_x, center_y = 50, 50
        eye_width = 60
        
        # Colors (matching main app's modern palette)
        bg_color = "#334155"        # Medium slate for outline
        iris_color = "#3b82f6"      # Blue for iris
        pupil_color = "#0f172a"     # Very dark slate for pupil
        highlight_color = "#f8fafc" # Lightest slate for highlight
        closed_eye_color = "#64748b" # Slate 500 for closed eye line
        white_sclera_color = "#e2e8f0" # Lighter slate for sclera
        
        eye_height = 40 # Default for "open"
        if self.eye_state == "open":
            eye_height = 40
        elif self.eye_state == "half":
            eye_height = 20 # Shorter height for half-closed
        else:  # closed
            # Draw closed eye (just a line representing the eyelid)
            self.eye_canvas.create_line(
                center_x - 30, center_y, # Start X, Start Y
                center_x + 30, center_y, # End X, End Y
                fill=closed_eye_color,
                width=3,
                smooth=True # Smooth the line for a better look
            )
            return # No need to draw iris/pupil if closed
            
        # Draw eye background (sclera/white part) as an oval
        self.eye_canvas.create_oval(
            center_x - eye_width//2, center_y - eye_height//2,
            center_x + eye_width//2, center_y + eye_height//2,
            fill=white_sclera_color, outline=bg_color, width=2
        )
        
        # Draw iris
        iris_size = min(eye_height - 10, 25) # Iris size scales with eye height, capped at 25
        self.eye_canvas.create_oval(
            center_x - iris_size//2, center_y - iris_size//2,
            center_x + iris_size//2, center_y + iris_size//2,
            fill=iris_color, outline="" # No outline for iris
        )
        
        # Draw pupil
        pupil_size = iris_size // 2
        self.eye_canvas.create_oval(
            center_x - pupil_size//2, center_y - pupil_size//2,
            center_x + pupil_size//2, center_y + pupil_size//2,
            fill=pupil_color, outline="" # No outline for pupil
        )
        
        # Draw highlight on the pupil for a shiny effect
        highlight_size = pupil_size // 3
        self.eye_canvas.create_oval(
            center_x - pupil_size//4, center_y - pupil_size//4,
            center_x - pupil_size//4 + highlight_size, center_y - pupil_size//4 + highlight_size,
            fill=highlight_color, outline=""
        )
