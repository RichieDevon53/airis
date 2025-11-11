# fixed_autogui_tools.py
import pyautogui
import time
from typing import Optional
from app.utils.prepareimage import prepare_images
from app.utils.screenshot import screenshot
from langchain.tools import tool

# Configure PyAutoGUI safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

class ScreenAutomationTools:
    """Enhanced screen automation tools with better error handling and capabilities"""
    
    @staticmethod
    def wait_for_element(timeout: int = 10) -> bool:
        """Wait for screen to stabilize after an action"""
        time.sleep(1)  # Basic wait - can be enhanced with image comparison
        return True

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
        screen_width, screen_height = pyautogui.size()
        if not (0 <= coordinate_x_cursor_target <= screen_width and 
                0 <= coordinate_y_cursor_target <= screen_height):
            raise ValueError(f"Coordinates ({coordinate_x_cursor_target}, {coordinate_y_cursor_target}) are outside screen boundaries ({screen_width}x{screen_height})")
        
        pyautogui.moveTo(coordinate_x_cursor_target, coordinate_y_cursor_target, duration=0.5)
        time.sleep(0.2)
        return f"Moved cursor to ({coordinate_x_cursor_target}, {coordinate_y_cursor_target})"
    except Exception as e:
        return f"Error moving cursor: {e}"

@tool
def CursorMoveAndClick(coordinate_x_cursor_target: int, coordinate_y_cursor_target: int, 
                     num_of_clicks: int = 1, secs_between_clicks: float = 0.1,
                     button: str = "left") -> str:
    """
    Move the cursor to specified coordinates and perform a click.
    
    Args:
        coordinate_x_cursor_target (int): The x-coordinate to move the cursor to
        coordinate_y_cursor_target (int): The y-coordinate to move the cursor to
        num_of_clicks (int): Number of clicks to perform
        secs_between_clicks (float): Delay between clicks in seconds
        button (str): Mouse button to click ('left', 'right', 'middle')
        
    Returns:
        str: Success message
    """
    try:
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
            duration=0.5
        )
        time.sleep(0.5)  # Wait for click to register
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
    return CursorMoveAndClick(
        coordinate_x_cursor_target, 
        coordinate_y_cursor_target, 
        num_of_clicks=2, 
        secs_between_clicks=0.1,
        duration=0.5
    )

@tool
def CursorRightClick(coordinate_x_cursor_target: int, coordinate_y_cursor_target: int) -> str:
    """
    Right-click at specified coordinates to open context menu.
    
    Args:
        coordinate_x_cursor_target (int): The x-coordinate to right-click
        coordinate_y_cursor_target (int): The y-coordinate to right-click
        duration (float): Duration of cursor movement
        
    Returns:
        str: Success message
    """
    return CursorMoveAndClick(
        coordinate_x_cursor_target, 
        coordinate_y_cursor_target, 
        button="right",
        duration=0.5
    )

@tool
def CursorDrag(coordinate_x_cursor_target: int, coordinate_y_cursor_target: int,
               num_seconds: float = 1.0, button: str = "left") -> str:
    """
    Drag the cursor from current position to specified coordinates.
    
    Args:
        coordinate_x_cursor_target (int): The x-coordinate to drag to
        coordinate_y_cursor_target (int): The y-coordinate to drag to
        num_seconds (float): Duration of drag movement in seconds
        button (str): Mouse button to drag with
        
    Returns:
        str: Success message
    """
    try:
        screen_width, screen_height = pyautogui.size()
        if not (0 <= coordinate_x_cursor_target <= screen_width and 
                0 <= coordinate_y_cursor_target <= screen_height):
            raise ValueError(f"Coordinates are outside screen boundaries")
        
        pyautogui.dragTo(
            coordinate_x_cursor_target, 
            coordinate_y_cursor_target, 
            duration=num_seconds,
            button=button
        )
        time.sleep(0.3)
        return f"Dragged to ({coordinate_x_cursor_target}, {coordinate_y_cursor_target})"
    except Exception as e:
        return f"Error dragging cursor: {e}"

@tool
def KeyboardWriteText(text_string: str) -> str:
    """
    Type text using the keyboard with configurable speed.
    
    Args:
        text_string (str): Text to type
        interval (float): Delay between keystrokes in seconds
        
    Returns:
        str: Success message
    """
    if not text_string:
        raise ValueError("Text string cannot be empty")
    
    try:
        pyautogui.write(text_string, interval=0.05)
        time.sleep(0.3)
        return f"Typed: '{text_string[:50]}{'...' if len(text_string) > 50 else ''}'"
    except Exception as e:
        return f"Error typing text: {e}"

@tool
def KeyboardPressKey(key: str, presses: int = 1) -> str:
    """
    Press a specific key multiple times.
    
    Args:
        key (str): Key to press (e.g., 'enter', 'tab', 'space', 'backspace', 'delete')
        presses (int): Number of times to press the key
        interval (float): Delay between key presses
        
    Returns:
        str: Success message
    """
    try:
        pyautogui.press(key, presses=presses, interval=0.05)
        time.sleep(0.2)
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
    if not hotkey_keys:
        raise ValueError("At least one key must be specified")
    
    try:
        # Split the hotkey string and execute
        keys = [key.strip() for key in hotkey_keys.split('+')]
        
        pyautogui.hotkey(*keys)
        time.sleep(0.5)
        return f"Executed hotkey: {hotkey_keys}"
    except Exception as e:
        return f"Error executing hotkey {hotkey_keys}: {e}"

@tool
def ScrollScreen(direction: str = "down", clicks: int = 3, x: Optional[int] = None, y: Optional[int] = None) -> str:
    """
    Scroll the screen in the specified direction.
    
    Args:
        direction (str): Direction to scroll ('up', 'down', 'left', 'right')
        clicks (int): Number of scroll clicks
        x (int, optional): X coordinate to scroll at (default: screen center)
        y (int, optional): Y coordinate to scroll at (default: screen center)
        
    Returns:
        str: Success message
    """
    try:
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
def WaitAndObserve(seconds: int = 2) -> str:
    """
    Wait for a specified duration and then take a screenshot.
    Useful for waiting for applications to load or actions to complete.
    
    Args:
        seconds (int): Number of seconds to wait
        
    Returns:
        str: Success message
    """
    try:
        time.sleep(float(int))
        return f"Waiting for {seconds} seconds..."
    except Exception as e:
        return f"Error during wait: {e}"

# Enhanced tool list with all capabilities
ToolBox = [
    ShowScreen,
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
]

if __name__ == "__main__":
    KeyboardHotkey({"hotkey_keys": "win+r"})
    KeyboardWriteText({"text_string": "chrome"})
    KeyboardPressKey({"key": "enter"})
