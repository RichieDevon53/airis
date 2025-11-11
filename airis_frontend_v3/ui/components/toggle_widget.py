# """
# Trapezoid toggle button component for slide-down frame functionality.
# Creates a trapezoid-shaped button at the bottom of the main window.
# """
# import tkinter as tk
# import math
# import pywinstyles

# class TrapezoidToggleButton:
#     """
#     Creates a trapezoid-shaped toggle button that slides a frame down/up.
#     """
    
#     def __init__(self, parent_app):
#         self.app = parent_app
#         self.root = parent_app.root
#         self.colors = parent_app.colors
        
#         # State management
#         self.is_expanded = False
#         self.is_animating = False
        
#         # UI components
#         self.button_window = None
#         self.slide_frame = None
#         self.canvas = None
        
#         # Animation settings
#         self.slide_speed = 15  # ms between animation frames
#         self.slide_step = 8    # pixels per frame
#         self.frame_height = 200  # height of the slide-down frame
        
#         # Button size
#         self.button_width = 120
#         self.button_height = 30
#         self.button_bottom_width = 80
        
#         self.create_button()
#         self.create_slide_frame()
        
#     def create_button(self):
#         """Creates the trapezoid button as a separate window."""
#         self.button_window = tk.Toplevel(self.root)
#         self.button_window.withdraw()  # Hide initially
        
#         # Configure button window
#         self.button_window.overrideredirect(True)
#         self.button_window.attributes('-topmost', True)
#         self.button_window.attributes('-alpha', 1)

#         transparent_color = '#010101'
#         self.button_window.attributes('-transparentcolor', transparent_color)
#         self.button_window.configure(bg=transparent_color)
        
#         self.canvas = tk.Canvas(
#             self.button_window,
#             width=self.button_width,
#             height=self.button_height,
#             highlightthickness=0,
#             bd=0,
#             bg=transparent_color
#         )
#         self.canvas.pack()
        
#         # Draw trapezoid shape
#         self.draw_trapezoid()
        
#         # Bind click event
#         self.canvas.bind("<Button-1>", self.on_button_click)
#         self.button_window.bind("<Button-1>", self.on_button_click)
        
#         # Add hover effects
#         self.canvas.bind("<Enter>", self.on_hover_enter)
#         self.canvas.bind("<Leave>", self.on_hover_leave)
        
#     def draw_trapezoid(self, is_hovered=False):
#         """Draws the trapezoid shape on the canvas."""
#         self.canvas.delete("trapezoid")
        
#         # Calculate trapezoid points
#         points = [
#             0, 0,
#             self.button_width, 0,
#             (self.button_width + self.button_bottom_width) // 2, self.button_height,
#             (self.button_width - self.button_bottom_width) // 2, self.button_height,
#         ]
        
#         # Choose colors based on state
#         if is_hovered:
#             fill_color = self.colors['accent_primary']
#         else:
#             fill_color = self.colors["icon_bg"]
        
#         # Draw trapezoid
#         self.canvas.create_polygon(
#             points,
#             fill=fill_color,
#             width=2,
#             tags="trapezoid"
#         )
        
#         # Add arrow indicator
#         arrow = "more" if not self.is_expanded else "▲"
#         text_color = 'white' if is_hovered else self.colors['border']
        
#         self.canvas.create_text(
#             self.button_width // 2, 10,
#             text=arrow,
#             fill=text_color,
#             font=('Arial', 10, 'bold'),
#             tags="trapezoid"
#         )
        
#     def create_slide_frame(self):
#         """Creates the slide-down frame."""
#         self.slide_frame = tk.Toplevel(self.root)
#         self.slide_frame.withdraw()  # Hide initially
        
#         # Configure slide frame
#         self.slide_frame.overrideredirect(True)
#         self.slide_frame.attributes('-topmost', False)  # Below main window
#         self.slide_frame.configure(bg=self.colors.get('bg_glass', '#1E1E1E'))
        
#         # Add some content to the slide frame
#         content_frame = tk.Frame(
#             self.slide_frame,
#             bg=self.colors.get('bg_glass', '#1E1E1E'),
#             relief='ridge',
#             bd=2
#         )
#         content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
#         # Sample content
#         title_label = tk.Label(
#             content_frame,
#             text="Extended Panel",
#             font=('Arial', 14, 'bold'),
#             bg=self.colors.get('bg_glass', '#1E1E1E'),
#             fg=self.colors.get('text_primary', '#FFFFFF')
#         )
#         title_label.pack(pady=(10, 5))
        
#         # Add some example content
#         for i in range(3):
#             item_frame = tk.Frame(
#                 content_frame,
#                 bg=self.colors.get('icon_bg', '#2A2A2A'),
#                 relief='flat',
#                 bd=1
#             )
#             item_frame.pack(fill='x', pady=2, padx=5)
            
#             tk.Label(
#                 item_frame,
#                 text=f"Option {i + 1}",
#                 bg=self.colors.get('icon_bg', '#2A2A2A'),
#                 fg=self.colors.get('text_secondary', '#CCCCCC'),
#                 font=('Arial', 10)
#             ).pack(side='left', padx=10, pady=5)
            
#             tk.Button(
#                 item_frame,
#                 text="Action",
#                 bg=self.colors.get('accent_primary', '#4A9EFF'),
#                 fg='white',
#                 relief='flat',
#                 bd=0,
#                 font=('Arial', 9),
#                 cursor='hand2'
#             ).pack(side='right', padx=10, pady=2)
        
#     def position_button(self):
#         """Positions the button at the bottom center tip of the main window."""
#         if not self.button_window:
#             return
            
#         # Get main window position and size
#         self.root.update_idletasks()
        
#         main_x = self.root.winfo_rootx()
#         main_y = self.root.winfo_rooty()
#         main_width = self.root.winfo_width()
#         main_height = self.root.winfo_height()
        
#         # Calculate button position (bottom center, at the tip of main window)
#         button_width = 120
#         button_height = 20
#         button_x = main_x + (main_width - button_width) // 2
        
#         # Position button so it starts exactly at the bottom edge of main window
#         # The button will extend downward from this point
#         button_y = main_y + main_height - 5
        
#         self.button_window.geometry(f"{button_width}x{button_height}+{button_x}+{button_y}")
       
#     def position_slide_frame(self):
#         """Positions the slide frame below the trapezoid button."""
#         if not self.slide_frame:
#             return
            
#         # Get main window position and size
#         self.root.update_idletasks()
        
#         main_x = self.root.winfo_rootx()
#         main_y = self.root.winfo_rooty()
#         main_width = self.root.winfo_width()
#         main_height = self.root.winfo_height()
        
#         # Position frame below the button (button height is 25px)
#         frame_x = main_x
#         frame_y = main_y + main_height + 25  # Below button with no gap
        
#         self.slide_frame.geometry(f"{main_width}x{self.frame_height}+{frame_x}+{frame_y}")
    
#     def show_button(self):
#         """Shows the trapezoid button when main window is visible."""
#         if self.app.is_window_visible and not self.app.is_processing:
#             self.position_button()
#             self.button_window.deiconify()
            
#     def hide_button(self):
#         """Hides the trapezoid button."""
#         if self.button_window:
#             self.button_window.withdraw()
#         if self.slide_frame and self.is_expanded:
#             self.slide_frame.withdraw()
#             self.is_expanded = False
#             self.draw_trapezoid()  # Reset arrow
            
#     def on_button_click(self, event=None):
#         """Handles button click to toggle slide frame."""
#         if self.is_animating:
#             return
            
#         if self.is_expanded:
#             self.slide_up()
#         else:
#             self.slide_down()
            
#     def slide_down(self):
#         """Animates the frame sliding down."""
#         if self.is_animating:
#             return
            
#         self.is_animating = True
#         self.is_expanded = True
        
#         # Position and show frame
#         self.position_slide_frame()
#         self.slide_frame.deiconify()
        
#         # Start with frame above its final position
#         self.root.update_idletasks()
#         main_y = self.root.winfo_rooty()
#         main_height = self.root.winfo_height()
        
#         start_y = main_y + main_height + 27 - self.frame_height
#         target_y = main_y + main_height + 27
        
#         self.animate_slide(start_y, target_y, True)
        
#     def slide_up(self):
#         """Animates the frame sliding up."""
#         if self.is_animating:
#             return
            
#         self.is_animating = True
#         self.is_expanded = False
        
#         # Get current position
#         self.root.update_idletasks()
#         main_y = self.root.winfo_rooty()
#         main_height = self.root.winfo_height()
        
#         start_y = main_y + main_height + 27
#         target_y = main_y + main_height + 27 - self.frame_height
        
#         self.animate_slide(start_y, target_y, False)
        
#     def animate_slide(self, start_y, target_y, sliding_down):
#         """Animates the sliding motion."""
#         current_geometry = self.slide_frame.geometry()
#         width_height = current_geometry.split('+')[0]  # Get "WIDTHxHEIGHT"
#         current_x = int(current_geometry.split('+')[1])
#         current_y = int(current_geometry.split('+')[2])
        
#         # Calculate next position
#         if sliding_down:
#             next_y = min(current_y + self.slide_step, target_y)
#         else:
#             next_y = max(current_y - self.slide_step, target_y)
            
#         # Update position
#         self.slide_frame.geometry(f"{width_height}+{current_x}+{next_y}")
        
#         # Continue animation or finish
#         if (sliding_down and next_y < target_y) or (not sliding_down and next_y > target_y):
#             self.root.after(self.slide_speed, lambda: self.animate_slide(start_y, target_y, sliding_down))
#         else:
#             # Animation finished
#             self.is_animating = False
#             if not sliding_down:
#                 self.slide_frame.withdraw()
            
#             # Update button appearance
#             self.draw_trapezoid()
            
#     def on_hover_enter(self, event):
#         """Handle mouse hover enter."""
#         self.draw_trapezoid(is_hovered=True)
        
#     def on_hover_leave(self, event):
#         """Handle mouse hover leave."""
#         self.draw_trapezoid(is_hovered=False)


# # Integration methods to add to the main app class:
# def integrate_trapezoid_button(app_instance):
#     """
#     Integration function to add trapezoid button to existing app.
#     Call this in the __init__ method of GlassEffectTrayApp.
#     """
#     # Add trapezoid button to app
#     app_instance.trapezoid_button = TrapezoidToggleButton(app_instance)
    
#     # Override existing window manager methods to handle button visibility
#     original_show = app_instance.window_manager.show_window_internal
#     original_hide = app_instance.window_manager.hide_window_internal
    
#     def enhanced_show():
#         original_show()
#         # Show button after window animation completes
#         app_instance.root.after(300, app_instance.trapezoid_button.show_button)
        
#     def enhanced_hide():
#         # Hide button before window hides
#         app_instance.trapezoid_button.hide_button()
#         original_hide()
        
#     # Replace methods
#     app_instance.window_manager.show_window_internal = enhanced_show
#     app_instance.window_manager.hide_window_internal = enhanced_hide
