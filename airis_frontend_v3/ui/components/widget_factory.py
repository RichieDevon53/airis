"""
Old Widget factory for creating UI components with consistent styling.
Handles the creation of all main UI widgets used in the application.
"""
import tkinter as tk

class WidgetFactory:
    """Factory class for creating consistently styled UI widgets."""
    
    def __init__(self, parent_app):
        self.app = parent_app
        self.root = parent_app.root
        self.colors = parent_app.colors
        self.fonts = parent_app.fonts
        
    def create_content_frame(self, parent):
        """Creates the main content frame."""
        search_container = tk.Frame(
            parent,
            bg=self.colors['bg_glass'],
            relief='flat',
            bd=0,
            highlightthickness=0
        )
        search_container.pack(fill='x')
        search_container.grid_columnconfigure(1, weight=1)
        
        # Search icon
        self.search_icon = tk.Label(
            search_container,
            text="🔍",
            font=self.fonts['icon'],
            bg=self.colors['bg_glass'],
            fg=self.colors['text_secondary']
        )
        self.search_icon.grid(row=0, column=0, padx=(25, 10), pady=5)
        
        separator1 = tk.Frame(
            search_container,
            bg=self.colors['border'],
            width=2,
            height=15
        )
        separator1.grid(row=0, column=1, sticky='ns', padx=(5, 15), pady=20)
        
        # Search input field
        self.search_entry = tk.Entry(
            search_container,
            font=self.fonts['input'],
            bg=self.colors['bg_glass'],
            fg=self.colors['text_primary'],
            relief='flat',
            bd=0,
            highlightthickness=0,
        )
        self.search_entry.grid(row=0, column=2, sticky='ew', ipady=15, ipadx=15)
        # self.search_entry.insert(0, "Search...")
        
        # Voice button with rounded appearance
        self.voice_button = tk.Button(
            search_container,
            text="🎤",
            font=self.fonts['icon'],
            bg=self.colors['icon_bg'],
            fg=self.colors['text_secondary'],
            relief='flat',
            bd=0,
            highlightthickness=0,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.on_voice_click
        )
        self.voice_button.grid(row=0, column=3, 
                               padx=(15, 0), pady=15
                               )
        
        # Drawing button
        self.drawing_button = tk.Button(
            search_container,
            text="🎨",
            font=self.fonts['icon'],
            bg=self.colors['icon_bg'],
            fg=self.colors['text_secondary'],
            activebackground=self.colors['accent_primary'],
            activeforeground='white',
            relief='flat',
            bd=0,
            highlightthickness=0,
            padx=15,
            pady=5,
            cursor='hand2',
            command=lambda: self.app.handle_enter(drawing_mode=True),
            state=tk.DISABLED
        )
        self.drawing_button.grid(row=0, column=4, 
                                 padx=15, pady=15
                                 )
        
        self.add_hover_effects()
        self.add_entry_events()
        
        return self.search_entry, self.drawing_button, self.voice_button
        
    def update_drawing_button_state(self, state):
        self.drawing_button.config(state=state)
        
    def add_hover_effects(self):
        """Adds hover effects to buttons."""
        def on_voice_enter(event):
            self.voice_button.config(
                bg=self.colors['accent_primary'],
                fg='white'
            )
            
        def on_voice_leave(event):
            self.voice_button.config(
                bg=self.colors['icon_bg'],
                fg=self.colors['text_secondary']
            )
            
        def on_drawing_enter(event):
            self.drawing_button.config(
                bg=self.colors['accent_primary'],
                fg='white'
            )
            
        def on_drawing_leave(event):
            self.drawing_button.config(
                bg=self.colors['icon_bg'],
                fg=self.colors['text_secondary']
            )
            
        self.voice_button.bind("<Enter>", on_voice_enter)
        self.voice_button.bind("<Leave>", on_voice_leave)
        self.drawing_button.bind("<Enter>", on_drawing_enter)
        self.drawing_button.bind("<Leave>", on_drawing_leave)
        
    def add_entry_events(self):
        """Adds events to the entry field."""
        def on_focus_in(event):
            if self.search_entry.get() == "Search...":
                self.search_entry.delete(0, tk.END)
                self.search_entry.config(fg=self.colors['text_primary'])
                
        def on_focus_out(event):
            if self.search_entry.get() == "":
                self.search_entry.insert(0, "Search...")
                self.search_entry.config(fg=self.colors['text_secondary'])
                
        def on_enter_key(event):
            self.on_search()
            
        self.search_entry.bind("<FocusIn>", on_focus_in)
        self.search_entry.bind("<FocusOut>", on_focus_out)
        self.search_entry.bind("<Return>", on_enter_key)
        
        self.search_entry.config(fg=self.colors['text_secondary'])
        
    def on_search(self):
        """Handle search action."""
        search_text = self.search_entry.get()
        if search_text and search_text != "Search...":
            print(f"Searching for: {search_text}")
        else:
            print("Please enter search text")
            
    def on_voice_click(self):
        """Handle voice button click."""
        print("Voice search activated!")
        
    def on_drawing_click(self):
        """Handle drawing button click."""
        from app.controllers import maincontroller
        maincontroller.controller.glass_board(self.search_entry.get().strip())
        