"""
Main entry point for the Airis application.
Handles initialization and starts the main application.
"""
import sys
import os
from .ui.main_window import GlassEffectTrayApp

def main():
    """Main application entry point."""
    try:
        app = GlassEffectTrayApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
