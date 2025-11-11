# fixed_autogui_tools.py
import pyautogui
import time
import json
import subprocess
import shlex
from pathlib import Path
from typing import Union, Dict, Any, Optional
from app.utils.prepareimage import prepare_images
from app.utils.screenshot import screenshot
from langchain.tools import tool

# Configure PyAutoGUI safety settings
pyautogui.FAILSAFE = True

class ScreenAutomationTools:
    """Enhanced screen automation tools with better error handling and capabilities"""
    
    @staticmethod
    def wait_for_element(timeout: int = 10) -> bool:
        """Wait for screen to stabilize after an action"""
        time.sleep(1)
        return True

@tool
def OpenApplication(app_name: str, wait_time: int = 2) -> str:
    """
    Open an application using the Run dialog (Win+R).
    This is a macro that combines: Win+R → Type app name → Enter
    
    Args:
        app_name (str): Name of the application to open (e.g., "chrome", "notepad", "calc")
        wait_time (int, optional): Seconds to wait after opening (default: 2)
    
    Returns:
        str: Success message
    """
    try:
        if not app_name:
            return "Error: app_name is required"
        
        # Execute the sequence
        pyautogui.hotkey('win', 'r')  # Open Run dialog
        time.sleep(0.3)  # Brief pause for dialog to open
        pyautogui.write(app_name, interval=0.05)  # Type app name
        pyautogui.press('enter')  # Press Enter
        time.sleep(wait_time)  # Wait for app to load
        
        return f"Opened application: {app_name}"
    except Exception as e:
        return f"Error opening application: {e}"

@tool
def OpenBrowserAndNavigate(url: str, browser: str = "chrome", wait_time: int = 3) -> str:
    """
    Open a browser and navigate to a specific URL.
    This is a macro that combines: Win+R → "chrome" → Enter → Wait → Type URL → Enter
    
    Args:
        url (str): URL to navigate to
        browser (str, optional): Browser to use (default: "chrome")
        wait_time (int, optional): Seconds to wait for browser to load (default: 3)
    
    Returns:
        str: Success message
    """
    try:
        if not url:
            return "Error: url is required"
        
        # Open browser
        pyautogui.hotkey('win', 'r')
        time.sleep(0.3)
        pyautogui.write(browser, interval=0.05)
        pyautogui.press('enter')
        time.sleep(wait_time)  # Wait for browser to load
        
        # Navigate to URL
        pyautogui.hotkey('ctrl', 'l')  # Focus address bar
        time.sleep(0.2)
        pyautogui.write(url, interval=0.05)
        pyautogui.press('enter')
        time.sleep(1)  # Wait for page to start loading
        
        return f"Opened {browser} and navigated to {url}"
    except Exception as e:
        return f"Error opening browser and navigating: {e}"

@tool
def SaveFile(filename: str, wait_time: float = 0.5) -> str:
    """
    Save a file using Ctrl+S dialog.
    This is a macro that combines: Ctrl+S → Type filename → Enter
    
    Args:
        filename (str): Name of the file to save
        wait_time (float, optional): Seconds to wait for dialog (default: 0.5)
    
    Returns:
        str: Success message
    """
    try:
        if not filename:
            return "Error: filename is required"
        
        # Execute save sequence
        pyautogui.hotkey('ctrl', 's')  # Open Save dialog
        time.sleep(wait_time)  # Wait for dialog
        pyautogui.write(filename, interval=0.05)  # Type filename
        pyautogui.press('enter')  # Save
        time.sleep(0.3)  # Brief pause
        
        return f"Saved file as: {filename}"
    except Exception as e:
        return f"Error saving file: {e}"

@tool
def SwitchWindowAndAct(action: Optional[str] = None, x: Optional[int] = None, y: Optional[int] = None) -> str:
    """
    Switch to another window and perform an action.
    This is a macro that combines: Alt+Tab → Optional action
    
    Args:
        action (str, optional): Action to perform after switching ("click", "space", "enter", or any key)
        x (int, optional): X coordinate to click (if action is "click")
        y (int, optional): Y coordinate to click (if action is "click")
    
    Returns:
        str: Success message
    """
    try:
        # Switch window
        pyautogui.hotkey('alt', 'tab')
        time.sleep(0.5)  # Wait for window switch
        
        # Perform optional action
        if action == 'click' and x is not None and y is not None:
            pyautogui.click(x, y)
            return f"Switched window and clicked at ({x}, {y})"
        elif action and action != 'click':
            pyautogui.press(action)
            return f"Switched window and pressed {action}"
        
        return "Switched to next window"
    except Exception as e:
        return f"Error switching window: {e}"

@tool
def CopyPasteText(destination_x: int, destination_y: int, wait_time: float = 0.3) -> str:
    """
    Copy selected text and paste it somewhere else.
    This is a macro that combines: Ctrl+C → Click location → Ctrl+V
    
    Args:
        destination_x (int): X coordinate where to paste
        destination_y (int): Y coordinate where to paste
        wait_time (float, optional): Time to wait between actions (default: 0.3)
    
    Returns:
        str: Success message
    """
    try:
        # Copy
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(wait_time)
        
        # Click destination and paste
        pyautogui.click(destination_x, destination_y)
        time.sleep(wait_time)
        pyautogui.hotkey('ctrl', 'v')
        
        return f"Copied and pasted text to ({destination_x}, {destination_y})"
    except Exception as e:
        return f"Error copying and pasting: {e}"

@tool
def OpenFileExplorer(path: Optional[str] = None) -> str:
    """
    Open Windows File Explorer.
    This is a simple macro for Win+E.
    
    Args:
        path (str, optional): Specific path to navigate to
    
    Returns:
        str: Success message
    """
    try:
        # Open File Explorer
        pyautogui.hotkey('win', 'e')
        time.sleep(1)  # Wait for explorer to open
        
        # Navigate to specific path if provided
        if path:
            pyautogui.hotkey('ctrl', 'l')  # Focus address bar
            time.sleep(0.2)
            pyautogui.write(path, interval=0.05)
            pyautogui.press('enter')
            time.sleep(0.5)
            return f"Opened File Explorer and navigated to: {path}"
        
        return "Opened File Explorer"
    except Exception as e:
        return f"Error opening File Explorer: {e}"

@tool
def ShowScreen() -> str:
    """
    Take a screenshot of the current screen and prepare the image.
    No parameters required.
    
    Returns: 
        str: base64 encoded image of the current screenshot
    """ 
    try:
        screenshot()
        result = prepare_images(is_direct=True)
        print("Screenshot taken successfully")
        return result
    except Exception as e:
        return f"Error taking screenshot: {e}"

@tool
def run_terminal(command: str, working_directory: str = ".", timeout: int = 60) -> str:
    """
    Executes a command in the terminal and returns its output.
    This tool is essential for file system operations, running scripts, and system interaction.

    Args:
        command (str): The command to be executed (e.g., "ls -l", "pip install numpy").
        working_directory (str, optional): The directory where the command should be run. Defaults to the current directory.
        timeout (int, optional): The maximum time in seconds to wait for the command to complete. Defaults to 60.

    Returns:
        str: The standard output (stdout) of the command if successful.
             If the command fails, it returns a detailed error message including the return code, stdout, and stderr.
             
    Example Usage:
    run_terminal(command="ls -l", working_directory="/home/user/project")
    run_terminal(command="git status")
    run_terminal(command="python --version")
    """
    try:
        if not command:
            return "Error: The 'command' parameter is missing."

        # Use shlex.split to handle command arguments safely, preventing shell injection
        command_parts = shlex.split(command)

        # Ensure the working directory exists
        if not Path(working_directory).is_dir():
            return f"Error: Working directory '{working_directory}' does not exist."

        process = subprocess.run(
            command_parts,
            capture_output=True,
            text=True,
            cwd=working_directory,
            timeout=timeout,
            check=False  # We set check=False to handle non-zero exit codes manually
        )

        if process.returncode == 0:
            # Command was successful
            output = process.stdout.strip()
            if not output:
                return f"Command '{command}' executed successfully with no output."
            return f"Success:\n{output}"
        else:
            # Command failed
            error_message = (
                f"Error: Command '{command}' failed with return code {process.returncode}.\n"
                f"--> STDOUT:\n{process.stdout.strip()}\n"
                f"--> STDERR:\n{process.stderr.strip()}"
            )
            return error_message

    except subprocess.TimeoutExpired:
        return f"Error: Command '{command}' timed out after {timeout} seconds."
    except FileNotFoundError:
        return f"Error: Command not found. Make sure '{command_parts[0]}' is installed and in your PATH."
    except Exception as e:
        return f"An unexpected error occurred: {e}"
    
@tool
def generate_directory_tree(start_path: str = '.', max_depth: int = 3) -> str:
    """
    Generates a string representation of a directory tree.

    Args:
        start_path (str): The path to the directory to start from.
        max_depth (int): The maximum depth to traverse.

    Returns:
        A string representing the directory tree.
    """
    
    resolved_path = Path(start_path).resolve()
    
    if not resolved_path.is_dir():
        return f"Error: {resolved_path} is not a valid directory."

    tree = f"{resolved_path.name}/\n"

    def _walk(directory: Path, prefix: str = "", depth: int = 0):
        nonlocal tree
        if depth >= max_depth:
            tree += f"{prefix}└── ... (max depth reached)\n"
            return

        contents = sorted(list(directory.iterdir()), key=lambda p: p.is_file())
        pointers = ["├── "] * (len(contents) - 1) + ["└── "]

        for pointer, path in zip(pointers, contents):
            tree += f"{prefix}{pointer}{path.name}\n"
            if path.is_dir():
                extension = "│   " if pointer == "├── " else "    "
                _walk(path, prefix=prefix + extension, depth=depth + 1)

    _walk(resolved_path)
    return tree

@tool
def CursorMove(coordinate_x_cursor_target: int, coordinate_y_cursor_target: int) -> str:
    """
    Move the cursor to specified coordinates on the screen.
    
    Args:
        coordinate_x_cursor_target (int): The x-coordinate to move the cursor to
        coordinate_y_cursor_target (int): The y-coordinate to move the cursor to
        
    Returns:
        str: Success message
    """
    try:
        duration = 0.2
        
        screen_width, screen_height = pyautogui.size()
        if not (0 <= coordinate_x_cursor_target <= screen_width and 
                0 <= coordinate_y_cursor_target <= screen_height):
            raise ValueError(f"Coordinates ({coordinate_x_cursor_target}, {coordinate_y_cursor_target}) are outside screen boundaries ({screen_width}x{screen_height})")
        
        pyautogui.moveTo(coordinate_x_cursor_target, coordinate_y_cursor_target, duration=duration)
        return f"Moved cursor to ({coordinate_x_cursor_target}, {coordinate_y_cursor_target})"
    except Exception as e:
        return f"Error moving cursor: {e}"

@tool
def CursorMoveAndClick(coordinate_x_cursor_target: int, coordinate_y_cursor_target: int, num_of_clicks: int = 1, secs_between_clicks: float = 0.1, button: str = 'left') -> str:
    """
    Move the cursor to specified coordinates and perform a click.
    
    Args:
        coordinate_x_cursor_target (int): The x-coordinate to move the cursor to
        coordinate_y_cursor_target (int): The y-coordinate to move the cursor to
        num_of_clicks (int, optional): Number of clicks to perform
        secs_between_clicks (float, optional): Delay between clicks in seconds
        button (str, optional): Mouse button to click ('left', 'right', 'middle')
    
    Returns:
        str: Success message
    """
    try:
        duration = 0.2
        
        screen_width, screen_height = pyautogui.size()
        if not (0 <= coordinate_x_cursor_target <= screen_width and 
                0 <= coordinate_y_cursor_target <= screen_height):
            raise ValueError(f"Coordinates ({coordinate_x_cursor_target}, {coordinate_y_cursor_target}) are outside screen boundaries")
        
        pyautogui.click(
            coordinate_x_cursor_target, 
            coordinate_y_cursor_target, 
            clicks=num_of_clicks, 
            interval=secs_between_clicks, 
            button=button,
            duration=duration
        )
        return f"Clicked at ({coordinate_x_cursor_target}, {coordinate_y_cursor_target}) with {button} button, {num_of_clicks} times"
    except Exception as e:
        return f"Error clicking: {e}"

@tool
def CursorDoubleClick(coordinate_x_cursor_target: int, coordinate_y_cursor_target: int) -> str:
    """
    Double-click at specified coordinates.
    
    Args:
        coordinate_x_cursor_target (int): The x-coordinate to double-click
        coordinate_y_cursor_target (int): The y-coordinate to double-click
    
    Returns:
        str: Success message
    """
    try:
        duration = 0.2
        
        return CursorMoveAndClick(
            coordinate_x_cursor_target=coordinate_x_cursor_target,
            coordinate_y_cursor_target=coordinate_y_cursor_target,
            num_of_clicks=2,
            secs_between_clicks=0.1
        )
    except Exception as e:
        return f"Error double-clicking: {e}"

@tool
def CursorRightClick(coordinate_x_cursor_target: int, coordinate_y_cursor_target: int) -> str:
    """
    Right-click at specified coordinates to open context menu.
    
    Args:
        coordinate_x_cursor_target (int): The x-coordinate to right-click
        coordinate_y_cursor_target (int): The y-coordinate to right-click
    
    Returns:
        str: Success message
    """
    try:
        duration = 0.2
        
        return CursorMoveAndClick(
            coordinate_x_cursor_target=coordinate_x_cursor_target,
            coordinate_y_cursor_target=coordinate_y_cursor_target,
            button='right'
        )
    except Exception as e:
        return f"Error right-clicking: {e}"

@tool
def CursorDrag(coordinate_x_cursor_target: int, coordinate_y_cursor_target: int, num_seconds: float = 1.0, button: str = 'left') -> str:
    """
    Drag the cursor from current position to specified coordinates.
    
    Args:
        coordinate_x_cursor_target (int): The x-coordinate to drag to
        coordinate_y_cursor_target (int): The y-coordinate to drag to
        num_seconds (float, optional): Duration of drag movement in seconds
        button (str, optional): Mouse button to drag with
    
    Returns:
        str: Success message
    """
    try:
        screen_width, screen_height = pyautogui.size()
        if not (0 <= coordinate_x_cursor_target <= screen_width and 
                0 <= coordinate_y_cursor_target <= screen_height):
            raise ValueError("Coordinates are outside screen boundaries")
        
        pyautogui.dragTo(
            coordinate_x_cursor_target, 
            coordinate_y_cursor_target, 
            duration=num_seconds,
            button=button
        )
        return f"Dragged to ({coordinate_x_cursor_target}, {coordinate_y_cursor_target})"
    except Exception as e:
        return f"Error dragging cursor: {e}"

@tool
def KeyboardWriteText(text: str) -> str:
    """
    Type text using the keyboard with configurable speed.
    
    Args:
        text (str): Text to type
    
    Returns:
        str: Success message
    """
    try:
        interval = 0.05
        
        if not text:
            raise ValueError("Text string cannot be empty")
        
        pyautogui.write(text, interval=interval)
        return f"Typed: '{text[:50]}{'...' if len(text) > 50 else ''}'"
    except Exception as e:
        return f"Error typing text: {e}"

@tool
def KeyboardPressKey(key: str, presses: int = 1) -> str:
    """
    Press a specific key multiple times.
    
    Args:
        key (str): Key to press (e.g., 'enter', 'tab', 'space', 'backspace', 'delete')
        presses (int, optional): Number of times to press the key
    
    Returns:
        str: Success message
    """
    try:
        interval = 0.05
        
        if not key:
            raise ValueError("Key cannot be empty")
        
        pyautogui.press(key, presses=presses, interval=interval)
        return f"Pressed '{key}' {presses} time(s)"
    except Exception as e:
        return f"Error pressing key '{key}': {e}"

@tool
def KeyboardHotkey(hotkey_keys: str) -> str:
    """
    Execute keyboard hotkey combinations.
    
    Args:
        hotkey_keys (str): Keys to press simultaneously, separated by '+' (e.g., 'ctrl+c', 'alt+tab', 'win+r')
    
    Examples:
        KeyboardHotkey('ctrl+c')  # Copy
        KeyboardHotkey('ctrl+v')  # Paste
        KeyboardHotkey('alt+tab')  # Switch windows
        KeyboardHotkey('win+r')   # Run dialog
        KeyboardHotkey('ctrl+shift+esc')  # Task Manager
        
    Returns:
        str: Success message
    """
    try:
        if not hotkey_keys:
            raise ValueError("At least one key must be specified")
        
        # Split the hotkey string and execute
        keys = [key.strip() for key in hotkey_keys.split('+')]
        
        pyautogui.hotkey(*keys)
        return f"Executed hotkey: {hotkey_keys}"
    except Exception as e:
        return f"Error executing hotkey {hotkey_keys}: {e}"

@tool
def ScrollScreen(direction: str = 'down', clicks: int = 3, x: Optional[int] = None, y: Optional[int] = None) -> str:
    """
    Scroll the screen in the specified direction.
    
    Args:
        direction (str, optional): Direction to scroll ('up', 'down')
        clicks (int, optional): Number of scroll clicks
        x (int, optional): X coordinate to scroll at (default: screen center)
        y (int, optional): Y coordinate to scroll at (default: screen center)
    
    Returns:
        str: Success message
    """
    try:
        scroll_x, scroll_y = x, y
        if scroll_x is None or scroll_y is None:
            screen_width, screen_height = pyautogui.size()
            scroll_x = screen_width // 2
            scroll_y = screen_height // 2
        
        if direction.lower() == "up":
            pyautogui.scroll(clicks, x=scroll_x, y=scroll_y)
        elif direction.lower() == "down":
            pyautogui.scroll(-clicks, x=scroll_x, y=scroll_y)
        else:
            raise ValueError("Direction must be 'up' or 'down'")
        
        time.sleep(0.3)
        return f"Scrolled {direction} {clicks} clicks at ({scroll_x}, {scroll_y})"
    except Exception as e:
        return f"Error scrolling: {e}"

@tool
def WaitAndObserve(seconds: int = 2) -> str:
    """
    Wait for a specified duration and then take a screenshot.
    Useful for waiting for applications to load or actions to complete.
    
    Args:
        seconds (int, optional): Number of seconds to wait
    
    Returns:
        str: Success message
    """
    try:
        time.sleep(seconds)
        return f"Waited for {seconds} seconds"
    except Exception as e:
        return f"Error during wait: {e}"

# Enhanced tool list with all capabilities
ToolBox = [
    ShowScreen,
    OpenApplication,
    OpenBrowserAndNavigate,
    SaveFile,
    SwitchWindowAndAct,
    CopyPasteText,
    OpenFileExplorer,
    CursorMove,
    CursorMoveAndClick,
    CursorDoubleClick,
    CursorRightClick,
    CursorDrag,
    KeyboardWriteText,
    KeyboardPressKey,
    KeyboardHotkey,
    ScrollScreen,
    WaitAndObserve,
    generate_directory_tree,
    run_terminal,
]
