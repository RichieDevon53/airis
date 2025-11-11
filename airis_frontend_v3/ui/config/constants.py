"""
UI constants and configuration for the Airis application.
Contains colors, dimensions, and other design constants.
"""
import platform

class UIConstants:
    """UI constants for consistent styling across the application."""
    
    # Window dimensions
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 200
    CORNER_RADIUS = 20
    BLUR_ALPHA = 1
    
    # Color scheme - Modern glass color palette
    COLORS = {
        'bg_glass': '#282931',    # White search bar
        'text_primary': '#D3D9E3',
        'text_secondary': '#D3D9E3',
        'accent_primary': '#6590FD',
        'border': '#61646D',
        'hover': '#f5f5f5',
        'icon_bg': '#2E2F37',
        'text_muted': '#7B7E87',    # Slate 500 (grayish)
        # 'transparant': '#00000000'
    }
    
    # Placeholder text
    PLACEHOLDER_TEXT = "Search..."
    
    @staticmethod
    def get_platform_font(root_widget):
        """
        Determines optimal font configuration based on the operating system.
        Includes a simplified DPI scaling attempt for better readability on high-DPI screens.
        """
        system = platform.system()
        base_size = 18
        
        # Scale font based on system DPI
        try:
            dpi = root_widget.winfo_fpixels('1i')
            scale_factor = dpi / 96.0
            base_size = int(base_size * max(1.0, min(scale_factor, 1.5)))
        except Exception:
            pass
            
        if system == "Windows":
            return {
                'input': ('Sans-serif', base_size + 4, 'normal'),
                'body': ('Segoe UI', base_size, 'normal'),
                'small': ('Segoe UI', base_size - 2, 'normal'),
                'mono': ('Consolas', base_size, 'normal'),
                'icon': ('Segoe UI Symbol', 20)
            }
        elif system == "Darwin":  # macOS
            return {
                'input': ('SF Pro Display', base_size + 4, 'normal'),
                'body': ('.AppleSystemUIFont', base_size, 'normal'),
                'small': ('.AppleSystemUIFont', base_size - 2, 'normal'),
                'mono': ('SF Mono', base_size, 'normal')
            }
        else:  # Linux
            return {
                'input': ('Inter', base_size + 4, 'normal'),
                'body': ('Inter', base_size, 'normal'),
                'small': ('Inter', base_size - 2, 'normal'),
                'mono': ('JetBrains Mono', base_size, 'normal')
            }
    
    @staticmethod
    def get_welcome_message():
        """Returns the welcome message for the response area."""
        return f"""Welcome to Airis! 🤖

This is your AI assistant interface. Type your question or request in the input field above and press Enter to get a response.

If you press Enter with an empty input, Airis will take a screenshot of your active screen and analyze it.

Features:
• Intelligent responses powered by AI
• Screenshot analysis capabilities (just press Enter!)
• Global hotkey support ({platform.system()}+Alt+Space)
• Auto-hide on focus loss
• Modern glassmorphism interface
• Blinking eye animation during processing

Ready to assist you!"""
