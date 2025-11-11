"""
Modern card-based History window for the Airis application.
Displays a sleek, card-based interface showing recent AI chat request history.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import webbrowser

class HistoryWindow:
    """Modern card-based history window with glassmorphism styling."""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.history_manager = app_instance.history_manager
        self.colors = {
            'bg_primary': "#5b5959",
            'bg_secondary': '#242424',
            'bg_card': '#2a2a2a',
            'bg_card_hover': '#323232',
            'bg_glass': 'rgba(255, 255, 255, 0.05)',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'text_muted': '#808080',
            'accent_primary': '#4a9eff',
            'accent_secondary': '#6366f1',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'border': '#404040'
        }
        self.fonts = {
            'title': ('Segoe UI', 18, 'bold'),
            'subtitle': ('Segoe UI', 14, 'normal'),
            'body': ('Segoe UI', 11, 'normal'),
            'body_bold': ('Segoe UI', 11, 'bold'),
            'small': ('Segoe UI', 9, 'normal'),
            'code': ('Consolas', 10, 'normal')
        }
        
        self.window = None
        self.canvas = None
        self.scrollable_frame = None
        self.selected_entry = None
        self.cards = []
        
        self.create_window()
    
    def create_window(self):
        """Creates and configures the history window."""
        self.window = tk.Toplevel(self.app.root)
        self.window.title("Request History")
        self.window.geometry("600x800")
        self.window.configure(bg=self.colors['bg_primary'])
        
        # Window styling
        self.window.attributes('-alpha', 0.88)
        self.window.resizable(True, True)
        self.window.minsize(900, 600)
        
        # Center the window
        self.center_window()
        
        # Create the main layout
        self.create_layout()
        
        # Load and display history
        self.refresh_history()
        
        # Bind events
        self.bind_events()
        
        # Focus the window
        self.window.lift()
        self.window.focus_set()
    
    
    def center_window(self):
        """Centers the window on screen."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_layout(self):
        """Creates the main layout of the history window."""
        # Main container with padding
        main_frame = tk.Frame(
            self.window, 
            bg=self.colors['bg_primary'],
            relief='flat'
            )
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header section
        self.create_header(main_frame)
        
        # Cards container with scrolling
        self.create_cards_container(main_frame)
        
        # Status section
        self.create_status_section(main_frame)
    
    def create_header(self, parent):
        """Creates the header section."""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Title and subtitle
        title_container = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        title_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(
            title_container,
            text="Request History",
            font=self.fonts['title'],
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        )
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(
            title_container,
            text="Your central hub for managing AI requests",
            font=self.fonts['subtitle'],
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        )
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
    
    def create_cards_container(self, parent):
        """Creates the scrollable cards container."""
        # Container frame
        container_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        container_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(
            container_frame,
            bg=self.colors['bg_primary'],
            highlightthickness=0,
            relief=tk.FLAT
        )
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            container_frame,
            orient="vertical",
            command=self.canvas.yview
        )
        
        # Scrollable frame
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg_primary'])
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
    
    def refresh_history(self):
        """Refreshes the history display."""
        # Clear existing cards
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.cards.clear()
        
        # Get filtered entries
        entries = self.get_entries()
        
        if not entries:
            # Show empty state
            empty_frame = tk.Frame(self.scrollable_frame, bg=self.colors['bg_primary'])
            empty_frame.pack(fill=tk.BOTH, expand=True, pady=50)
            
            empty_label = tk.Label(
                empty_frame,
                text="📋 No history entries found",
                font=self.fonts['subtitle'],
                fg=self.colors['text_muted'],
                bg=self.colors['bg_primary']
            )
            empty_label.pack()
            
            empty_desc = tk.Label(
                empty_frame,
                text="Your AI request history will appear here",
                font=self.fonts['body'],
                fg=self.colors['text_muted'],
                bg=self.colors['bg_primary']
            )
            empty_desc.pack(pady=(10, 0))
        else:
            # Create cards for each entry
            for entry in entries:
                self.create_card(entry, self.scrollable_frame)
        
        self.update_status(f"Displaying {len(entries)} entries")
    
    def get_entries(self):
        """Gets entries based on current search and filter."""
        entries = self.history_manager.get_recent_entries(100)
        return entries
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_status_section(self, parent):
        """Creates the status section."""
        status_frame = tk.Frame(parent, bg=self.colors['bg_card'], height=50)
        status_frame.pack(fill=tk.X)
        status_frame.pack_propagate(False)
        
        # Status info
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            font=self.fonts['body'],
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_card']
        )
        self.status_label.pack(side=tk.LEFT, padx=15, pady=15)
        
        # Statistics
        stats = self.history_manager.get_statistics()
        stats_text = f"Total: {stats['total_entries']} • Completed: {stats['completed_entries']} • Errors: {stats['error_entries']}"
        
        stats_label = tk.Label(
            status_frame,
            text=stats_text,
            font=self.fonts['body'],
            fg=self.colors['text_muted'],
            bg=self.colors['bg_card']
        )
        stats_label.pack(side=tk.RIGHT, padx=15, pady=15)
    
    def create_card(self, entry, parent):
        """Creates a single history card."""
        # Card frame with hover effect
        card_frame = tk.Frame(
            parent,
            bg=self.colors['bg_card'],
            relief=tk.FLAT,
            bd=1
        )
        card_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
        
        # Add hover effects
        def on_enter(e):
            card_frame.configure(bg=self.colors['bg_card_hover'])
            for child in card_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(bg=self.colors['bg_card_hover'])
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, (tk.Label, tk.Frame)):
                            grandchild.configure(bg=self.colors['bg_card_hover'])
        
        def on_leave(e):
            card_frame.configure(bg=self.colors['bg_card'])
            for child in card_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(bg=self.colors['bg_card'])
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, (tk.Label, tk.Frame)):
                            grandchild.configure(bg=self.colors['bg_card'])
        
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        card_frame.bind("<Button-1>", lambda e, entry=entry: self.select_card(entry))
        
        # Card content with padding
        content_frame = tk.Frame(card_frame, bg=self.colors['bg_card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Top row - Status and timestamp
        top_row = tk.Frame(content_frame, bg=self.colors['bg_card'])
        top_row.pack(fill=tk.X, pady=(0, 10))
        
        # Status indicator
        status_colors = {
            'completed': self.colors['success'],
            'error': self.colors['error'],
            'processing': self.colors['warning']
        }
        
        status_frame = tk.Frame(top_row, bg=self.colors['bg_card'])
        status_frame.pack(side=tk.LEFT)
        
        status_dot = tk.Label(
            status_frame,
            text="●",
            font=('Segoe UI', 12, 'bold'),
            fg=status_colors.get(entry.status, self.colors['text_muted']),
            bg=self.colors['bg_card']
        )
        status_dot.pack(side=tk.LEFT, padx=(0, 8))
        
        # Query type and status
        type_icons = {
            'text': '💬',
            'screenshot': '📸',
            'image': '🖼️'
        }
        
        type_text = f"{type_icons.get(entry.query_type, '📄')} {entry.query_type.title()}"
        if entry.status == 'completed':
            type_text += " • Completed"
        elif entry.status == 'error':
            type_text += " • Error"
        else:
            type_text += " • Processing"
        
        type_label = tk.Label(
            status_frame,
            text=type_text,
            font=self.fonts['body_bold'],
            fg=self.colors['text_primary'],
            bg=self.colors['bg_card']
        )
        type_label.pack(side=tk.LEFT)
        
        # Timestamp
        try:
            dt = datetime.strptime(entry.timestamp, "%Y-%m-%d %H:%M:%S")
            time_str = dt.strftime("%b %d, %I:%M %p")
        except:
            time_str = entry.timestamp
        
        time_label = tk.Label(
            top_row,
            text=time_str,
            font=self.fonts['small'],
            fg=self.colors['text_muted'],
            bg=self.colors['bg_card']
        )
        time_label.pack(side=tk.RIGHT)
        
        # Query text
        query_text = entry.query[:120] + "..." if len(entry.query) > 120 else entry.query
        query_label = tk.Label(
            content_frame,
            text=query_text,
            font=self.fonts['body'],
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_card'],
            justify=tk.LEFT,
            wraplength=800
        )
        query_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Bottom row - Duration and tokens
        bottom_row = tk.Frame(content_frame, bg=self.colors['bg_card'])
        bottom_row.pack(fill=tk.X)
        
        # Duration
        duration_label = tk.Label(
            bottom_row,
            text=f"⏱️ {entry.duration:.1f}s",
            font=self.fonts['small'],
            fg=self.colors['text_muted'],
            bg=self.colors['bg_card']
        )
        duration_label.pack(side=tk.LEFT)
        
        # Tokens
        if hasattr(entry, 'tokens_used') and entry.tokens_used:
            tokens_label = tk.Label(
                bottom_row,
                text=f"🔢 {entry.tokens_used} tokens",
                font=self.fonts['small'],
                fg=self.colors['text_muted'],
                bg=self.colors['bg_card']
            )
            tokens_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # Action buttons
        action_frame = tk.Frame(bottom_row, bg=self.colors['bg_card'])
        action_frame.pack(side=tk.RIGHT)
        
        # Copy button
        copy_btn = tk.Button(
            action_frame,
            text="📋",
            command=lambda: self.copy_response(entry),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary'],
            font=self.fonts['small'],
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor='hand2'
        )
        copy_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Delete button
        delete_btn = tk.Button(
            action_frame,
            text="🗑️",
            command=lambda: self.delete_entry(entry),
            bg=self.colors['error'],
            fg=self.colors['text_primary'],
            font=self.fonts['small'],
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor='hand2'
        )
        delete_btn.pack(side=tk.LEFT)
        
        # Store card reference
        self.cards.append((card_frame, entry))
        
        return card_frame
    
    
    def on_search_change(self, event=None):
        """Handles search text changes."""
        self.refresh_history()
    
    def on_filter_change(self, event=None):
        """Handles filter changes."""
        self.refresh_history()
    
    def select_card(self, entry):
        """Handles card selection."""
        self.selected_entry = entry
        self.show_full_response_dialog()
    
    def show_full_response_dialog(self):
        """Shows the full response in a dialog."""
        if not self.selected_entry:
            return
        
        dialog = tk.Toplevel(self.window)
        dialog.title(f"Response Details")
        dialog.geometry("900x700")
        dialog.configure(bg=self.colors['bg_primary'])
        
        # Header
        header_frame = tk.Frame(dialog, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 0))
        
        title_label = tk.Label(
            header_frame,
            text="Response Details",
            font=self.fonts['title'],
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        )
        title_label.pack(anchor=tk.W)
        
        # Details
        details_frame = tk.Frame(dialog, bg=self.colors['bg_card'])
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Response text
        text_widget = tk.Text(
            details_frame,
            font=self.fonts['body'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_primary'],
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        
        # Scrollbar for text
        text_scrollbar = ttk.Scrollbar(details_frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=text_scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=15, padx=(0, 15))
        
        # Insert content
        content = f"Query: {self.selected_entry.query}\n\n"
        content += f"Response:\n{self.selected_entry.response}"
        text_widget.insert(1.0, content)
        text_widget.config(state=tk.DISABLED)
    
    def copy_response(self, entry):
        """Copies the response to clipboard."""
        self.window.clipboard_clear()
        self.window.clipboard_append(entry.response)
        self.update_status("Response copied to clipboard")
    
    def delete_entry(self, entry):
        """Deletes an entry."""
        if messagebox.askyesno("Confirm Delete", "Delete this entry?", parent=self.window):
            self.history_manager.delete_entry(entry.id)
            self.refresh_history()
            self.update_status("Entry deleted")
    
    
    def update_status(self, message):
        """Updates the status."""
        self.status_label.config(text=message)
        self.window.after(3000, lambda: self.status_label.config(text="Ready"))
    
    def bind_events(self):
        """Binds window events."""
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        self.window.bind('<Escape>', lambda e: self.close_window())
        self.window.bind('<F5>', lambda e: self.refresh_history())
        
        # Bind mousewheel to canvas
        def bind_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        def unbind_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.canvas.bind('<Enter>', bind_mousewheel)
        self.canvas.bind('<Leave>', unbind_mousewheel)
    
    def close_window(self):
        """Closes the history window."""
        self.window.destroy()
    
    def show(self):
        """Shows the history window."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_set()
        else:
            self.create_window()