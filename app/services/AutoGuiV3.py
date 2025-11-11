# fixed_autogui_tools.py
import pyautogui
import time
import json
import subprocess
import shlex
from pathlib import Path
from typing import Union, Dict, Any
from app.utils.prepareimage import prepare_images
from app.utils.screenshot import screenshot
from langchain.tools import tool

# Configure PyAutoGUI safety settings
pyautogui.FAILSAFE = True

def parse_tool_input(tool_input: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parse tool input that might come as JSON string or dict.
    This handles the agent's parameter passing inconsistencies.
    """
    if isinstance(tool_input, str):
        try:
            return json.loads(tool_input)
        except json.JSONDecodeError:
            return {"value": tool_input}
    elif isinstance(tool_input, dict):
        return tool_input
    else:
        return {"value": tool_input}

class ScreenAutomationTools:
    """Enhanced screen automation tools with better error handling and capabilities"""
    
    @staticmethod
    def wait_for_element(timeout: int = 10) -> bool:
        """Wait for screen to stabilize after an action"""
        time.sleep(1)
        return True

@tool
def OpenApplication(tool_input: Union[str, Dict[str, Any]]) -> str:
    """
    Open an application using the Run dialog (Win+R).
    This is a macro that combines: Win+R → Type app name → Enter
    
    Args:
        tool_input: JSON string or dict containing:
            - app_name (str): Name of the application to open (e.g., "chrome", "notepad", "calc")
            - wait_time (int, optional): Seconds to wait after opening (default: 2)
    
    Returns:
        str: Success message
    """
    try:
        params = parse_tool_input(tool_input)
        app_name = params.get('app_name') or params.get('value', '')
        wait_time = int(params.get('wait_time', 2))
        
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
def OpenBrowserAndNavigate(tool_input: Union[str, Dict[str, Any]]) -> str:
    """
    Open a browser and navigate to a specific URL.
    This is a macro that combines: Win+R → "chrome" → Enter → Wait → Type URL → Enter
    
    Args:
        tool_input: JSON string or dict containing:
            - url (str): URL to navigate to
            - browser (str, optional): Browser to use (default: "chrome")
            - wait_time (int, optional): Seconds to wait for browser to load (default: 3)
    
    Returns:
        str: Success message
    """
    try:
        params = parse_tool_input(tool_input)
        url = params.get('url', '')
        browser = params.get('browser', 'chrome')
        wait_time = int(params.get('wait_time', 3))
        
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
def SaveFile(tool_input: Union[str, Dict[str, Any]]) -> str:
    """
    Save a file using Ctrl+S dialog.
    This is a macro that combines: Ctrl+S → Type filename → Enter
    
    Args:
        tool_input: JSON string or dict containing:
            - filename (str): Name of the file to save
            - wait_time (float, optional): Seconds to wait for dialog (default: 0.5)
    
    Returns:
        str: Success message
    """
    try:
        params = parse_tool_input(tool_input)
        filename = params.get('filename', '')
        wait_time = float(params.get('wait_time', 0.5))
        
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
def SwitchWindowAndAct(tool_input: Union[str, Dict[str, Any]]) -> str:
    """
    Switch to another window and perform an action.
    This is a macro that combines: Alt+Tab → Optional action
    
    Args:
        tool_input: JSON string or dict containing:
            - action (str, optional): Action to perform after switching ("click", "space", "enter", or any key)
            - x (int, optional): X coordinate to click (if action is "click")
            - y (int, optional): Y coordinate to click (if action is "click")
    
    Returns:
        str: Success message
    """
    try:
        params = parse_tool_input(tool_input)
        action = params.get('action', '')
        x = params.get('x')
        y = params.get('y')
        
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
def CopyPasteText(tool_input: Union[str, Dict[str, Any]]) -> str:
    """
    Copy selected text and paste it somewhere else.
    This is a macro that combines: Ctrl+C → Click location → Ctrl+V
    
    Args:
        tool_input: JSON string or dict containing:
            - destination_x (int): X coordinate where to paste
            - destination_y (int): Y coordinate where to paste
            - wait_time (float, optional): Time to wait between actions (default: 0.3)
    
    Returns:
        str: Success message
    """
    try:
        params = parse_tool_input(tool_input)
        dest_x = int(params.get('destination_x', 0))
        dest_y = int(params.get('destination_y', 0))
        wait_time = float(params.get('wait_time', 0.3))
        
        # Copy
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(wait_time)
        
        # Click destination and paste
        pyautogui.click(dest_x, dest_y)
        time.sleep(wait_time)
        pyautogui.hotkey('ctrl', 'v')
        
        return f"Copied and pasted text to ({dest_x}, {dest_y})"
    except Exception as e:
        return f"Error copying and pasting: {e}"

@tool
def OpenFileExplorer(tool_input: Union[str, Dict[str, Any]] = "") -> str:
    """
    Open Windows File Explorer.
    This is a simple macro for Win+E.
    
    Args:
        tool_input: JSON string or dict containing:
            - path (str, optional): Specific path to navigate to
    
    Returns:
        str: Success message
    """
    try:
        params = parse_tool_input(tool_input) if tool_input else {}
        path = params.get('path', '')
        
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
def ShowScreen(tool_input: str = "") -> str:
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

def run_terminal(tool_input: Union[str, Dict[str, Any]]) -> str:
    """
    Executes a command in the terminal and returns its output.
    This tool is essential for file system operations, running scripts, and system interaction.

    Args:
        tool_input: A JSON string or a dictionary containing the command details.
            - "command" (str): The command to be executed (e.g., "ls -l", "pip install numpy").
            - "working_directory" (str, optional): The directory where the command should be run. Defaults to the current directory.
            - "timeout" (int, optional): The maximum time in seconds to wait for the command to complete. Defaults to 60.

    Returns:
        str: The standard output (stdout) of the command if successful.
             If the command fails, it returns a detailed error message including the return code, stdout, and stderr.
             
    Example Usage:
    run_terminal('{"command": "ls -l", "working_directory": "/home/user/project"}')
    run_terminal('{"command": "git status"}')
    run_terminal("python --version")
    """
    try:
        params = parse_tool_input(tool_input)
        command = params.get("command")
        working_directory = params.get("working_directory", ".")
        timeout = int(params.get("timeout", 60))

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
def generate_directory_tree(tool_input: Union[str, Dict[str, Any]]) -> str:
    """
    Generates a string representation of a directory tree.

    Args:
        tool_input: JSON string or dict containing:
            start_path: The path to the directory to start from.
            max_depth: The maximum depth to traverse.

    Returns:
        A string representing the directory tree.
    """
    
    params = parse_tool_input(tool_input)
    start_path = Path(params.get('start_path', '.')).resolve()
    max_depth = params.get('max_depth', 3)
    
    if not start_path.is_dir():
        return f"Error: {start_path} is not a valid directory."

    tree = f"{start_path.name}/\n"

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

    _walk(start_path)
    return tree

@tool
def CursorMove(tool_input: Union[str, Dict[str, Any]]) -> str:
    """
    Move the cursor to specified coordinates on the screen.
    
    Args:
        tool_input: JSON string or dict containing:
            - coordinate_x_cursor_target (int): The x-coordinate to move the cursor to
            - coordinate_y_cursor_target (int): The y-coordinate to move the cursor to
        
    Returns:
        str: Success message
    """
    try:
        params = parse_tool_input(tool_input)
        
        coordinate_x_cursor_target = int(params.get('coordinate_x_cursor_target', 0))
        coordinate_y_cursor_target = int(params.get('coordinate_y_cursor_target', 0))
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
def CursorMoveAndClick(tool_input: Union[str, Dict[str, Any]]) -> str:
    """
    Move the cursor to specified coordinates and perform a click.
    
    Args:
        tool_input: JSON string or dict containing:
            - coordinate_x_cursor_target (int): The x-coordinate to move the cursor to
            - coordinate_y_cursor_target (int): The y-coordinate to move the cursor to
            - num_of_clicks (int, optional): Number of clicks to perform
            - secs_between_clicks (float, optional): Delay between clicks in seconds
            - button (str, optional): Mouse button to click ('left', 'right', 'middle')
        
    Returns:
        str: Success message
    """
    try:
        params = parse_tool_input(tool_input)
        
        coordinate_x_cursor_target = int(params.get('coordinate_x_cursor_target', 0))
        coordinate_y_cursor_target = int(params.get('coordinate_y_cursor_target', 0))
        num_of_clicks = int(params.get('num_of_clicks', 1))
        secs_between_clicks = float(params.get('secs_between_clicks', 0.1))
        button = params.get('button', 'left')
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
def CursorDoubleClick(tool_input: Union[str, Dict[str, Any]]) -> str:
    """
    Double-click at specified coordinates.
    
    Args:
        tool_input: JSON string or dict containing:
            - coordinate_x_cursor_target (int): The x-coordinate to double-click
            - coordinate_y_cursor_target (int): The y-coordinate to double-click
        
    Returns:
        str: Success message
    """
    try:
        params = parse_tool_input(tool_input)
        
        coordinate_x_cursor_target = int(params.get('coordinate_x_cursor_target', 0))
        coordinate_y_cursor_target = int(params.get('coordinate_y_cursor_target', 0))
        duration = 0.2
        
        return CursorMoveAndClick({
            'coordinate_x_cursor_target': coordinate_x_cursor_target,
            'coordinate_y_cursor_target': coordinate_y_cursor_target,
            'num_of_clicks': 2,
            'secs_between_clicks': 0.1,
            'duration': duration
        })
    except Exception as e:
        return f"Error double-clicking: {e}"

@tool
def CursorRightClick(tool_input: Union[str, Dict[str, Any]]) -> str:
    """
    Right-click at specified coordinates to open context menu.
    
    Args:
        tool_input: JSON string or dict containing:
            - coordinate_x_cursor_target (int): The x-coordinate to right-click
            - coordinate_y_cursor_target (int): The y-coordinate to right-click
        
    Returns:
        str: Success message
    """
    try:
        params = parse_tool_input(tool_input)
        
        coordinate_x_cursor_target = int(params.get('coordinate_x_cursor_target', 0))
        coordinate_y_cursor_target = int(params.get('coordinate_y_cursor_target', 0))
        duration = 0.2
        
        return CursorMoveAndClick({
            'coordinate_x_cursor_target': coordinate_x_cursor_target,
            'coordinate_y_cursor_target': coordinate_y_cursor_target,
            'button': 'right',
            'duration': duration
        })
    except Exception as e:
        return f"Error right-clicking: {e}"

@tool
def CursorDrag(tool_input: Union[str, Dict[str, Any]]) -> str:
    """
    Drag the cursor from current position to specified coordinates.
    
    Args:
        tool_input: JSON string or dict containing:
            - coordinate_x_cursor_target (int): The x-coordinate to drag to
            - coordinate_y_cursor_target (int): The y-coordinate to drag to
            - num_seconds (float, optional): Duration of drag movement in seconds
            - button (str, optional): Mouse button to drag with
        
    Returns:
        str: Success message
    """
    try:
        params = parse_tool_input(tool_input)
        
        coordinate_x_cursor_target = int(params.get('coordinate_x_cursor_target', 0))
        coordinate_y_cursor_target = int(params.get('coordinate_y_cursor_target', 0))
        num_seconds = float(params.get('num_seconds', 1.0))
        button = params.get('button', 'left')
        
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
def KeyboardWriteText(tool_input: Union[str, Dict[str, Any]]) -> str:
    """
    Type text using the keyboard with configurable speed.
    
    Args:
        tool_input: JSON string or dict containing:
            - text_string (str): Text to type
        
    Returns:
        str: Success message
    """
    try:
        params = parse_tool_input(tool_input)
        
        # Handle both parameter formats
        text_string = params.get('text_string') or params.get('value', '')
        interval = 0.05
        
        if not text_string:
            raise ValueError("Text string cannot be empty")
        
        pyautogui.write(text_string, interval=interval)
        return f"Typed: '{text_string[:50]}{'...' if len(text_string) > 50 else ''}'"
    except Exception as e:
        return f"Error typing text: {e}"

@tool
def KeyboardPressKey(tool_input: Union[str, Dict[str, Any]]) -> str:
    """
    Press a specific key multiple times.
    
    Args:
        tool_input: JSON string or dict containing:
            - key (str): Key to press (e.g., 'enter', 'tab', 'space', 'backspace', 'delete')
            - presses (int, optional): Number of times to press the key
        
    Returns:
        str: Success message
    """
    try:
        params = parse_tool_input(tool_input)
        
        # Handle both parameter formats
        key = params.get('key') or params.get('value', '')
        presses = int(params.get('presses', 1))
        interval = 0.05
        
        if not key:
            raise ValueError("Key cannot be empty")
        
        pyautogui.press(key, presses=presses, interval=interval)
        return f"Pressed '{key}' {presses} time(s)"
    except Exception as e:
        return f"Error pressing key '{key}': {e}"

@tool
def KeyboardHotkey(tool_input: Union[str, Dict[str, Any]]) -> str:
    """
    Execute keyboard hotkey combinations.
    
    Args:
        tool_input: JSON string or dict containing:
            - hotkey_keys (str): Keys to press simultaneously, separated by '+' (e.g., 'ctrl+c', 'alt+tab', 'win+r')
        
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
        params = parse_tool_input(tool_input)
        
        # Handle both parameter formats
        hotkey_keys = params.get('hotkey_keys') or params.get('value', '')
        
        if not hotkey_keys:
            raise ValueError("At least one key must be specified")
        
        # Split the hotkey string and execute
        keys = [key.strip() for key in hotkey_keys.split('+')]
        
        pyautogui.hotkey(*keys)
        return f"Executed hotkey: {hotkey_keys}"
    except Exception as e:
        return f"Error executing hotkey {hotkey_keys}: {e}"

@tool
def ScrollScreen(tool_input: Union[str, Dict[str, Any]] = "") -> str:
    """
    Scroll the screen in the specified direction.
    
    Args:
        tool_input: JSON string or dict containing:
            - direction (str, optional): Direction to scroll ('up', 'down', 'left', 'right')
            - clicks (int, optional): Number of scroll clicks
            - x (int, optional): X coordinate to scroll at (default: screen center)
            - y (int, optional): Y coordinate to scroll at (default: screen center)
        
    Returns:
        str: Success message
    """
    try:
        params = parse_tool_input(tool_input) if tool_input else {}
        
        direction = params.get('direction', 'down')
        clicks = int(params.get('clicks', 3))
        x = params.get('x')
        y = params.get('y')
        
        if x is None or y is None:
            screen_width, screen_height = pyautogui.size()
            x = screen_width // 2
            y = screen_height // 2
        
        if direction.lower() == "up":
            pyautogui.scroll(clicks, x=x, y=y)
        elif direction.lower() == "down":
            pyautogui.scroll(-clicks, x=x, y=y)
        else:
            raise ValueError("Direction must be 'up' or 'down'")
        
        time.sleep(0.3)
        return f"Scrolled {direction} {clicks} clicks at ({x}, {y})"
    except Exception as e:
        return f"Error scrolling: {e}"

@tool
def WaitAndObserve(tool_input: Union[str, Dict[str, Any]] = "") -> str:
    """
    Wait for a specified duration and then take a screenshot.
    Useful for waiting for applications to load or actions to complete.
    
    Args:
        tool_input: JSON string or dict containing:
            - seconds (int, optional): Number of seconds to wait
        
    Returns:
        str: Success message
    """
    try:
        params = parse_tool_input(tool_input) if tool_input else {}
        seconds = int(params.get('seconds', 2))
        
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
    
]
