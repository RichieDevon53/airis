import pyautogui
from typing import List
from app.utils.screenshot import gettemp
from app.utils.prepareimage import prepare_images
from app.utils.screenshot import screenshot
from langchain.tools import tool

@tool
def ShowScreen():
    """
Take a screenshot of the current screen and prepare the image.

Returns: 
    str: base64 encoded image of the current screenshot
""" 
    screenshot()
    return prepare_images(is_direct=True)

@tool
def CursorMove(
    coordinate_x_cursor_target: int, 
    coordinate_y_cursor_target: int, 
    ):
    """
    Move the cursor to specified coordinates on the screen.
    Args:
        coordinate_x_cursor_target (int): The x-coordinate to move the cursor to
        coordinate_y_cursor_target (int): The y-coordinate to move the cursor to

    Returns:
        str: Success message if movement completed

    Raises:
        ValueError: If target coordinates are outside screen boundaries
    """
    if not pyautogui.onScreen(coordinate_x_cursor_target, coordinate_y_cursor_target):
        raise ValueError("Target coordinates are outside the screen boundaries.")
    try:
        pyautogui.moveTo(
            coordinate_x_cursor_target, 
            coordinate_y_cursor_target, 
            1, 
            )
        print(f"move cursor to {coordinate_x_cursor_target}, {coordinate_y_cursor_target}")
        return ShowScreen()
    except Exception as e:
        return f"Error - Failed to move cursor: {e}"
    
@tool
def CursorMoveAndClick(
    coordinate_x_cursor_target: int, 
    coordinate_y_cursor_target: int, 
    num_of_clicks: int = 1, 
    secs_between_clicks: float = 0.0,
    button: str = "left",
    ):
    """
    Move the cursor to specified coordinates on the screen and perform a click.

    Args:
        coordinate_x_cursor_target (int): The x-coordinate to move the cursor to
        coordinate_y_cursor_target (int): The y-coordinate to move the cursor to
        num_of_clicks (int, optional): Number of clicks to perform. Defaults to 1
        secs_between_clicks (float, optional): Delay between clicks in seconds. Defaults to 0.0
        button (str, optional): Mouse button to click ('left', 'right', 'middle'). Defaults to 'left'

    Returns:
        str: Success message if movement completed

    Raises:
        ValueError: If target coordinates are outside screen boundaries
    """
    if not pyautogui.onScreen(coordinate_x_cursor_target, coordinate_y_cursor_target):
        raise ValueError("Target coordinates are outside the screen boundaries.")
    try:
        # pyautogui.moveTo(coordinate_x_cursor_target, coordinate_y_cursor_target, duration)
        pyautogui.click(
            coordinate_x_cursor_target, 
            coordinate_y_cursor_target, 
            1, 
            clicks=num_of_clicks, 
            interval=secs_between_clicks, 
            button=button
            )
        print(f"move and click cursor to {coordinate_x_cursor_target}, {coordinate_y_cursor_target}")
        return ShowScreen()
    except Exception as e:
        return f"Error - Failed to move cursor: {e}"
    
@tool
def CursorDrag(    
    coordinate_x_cursor_target: int, 
    coordinate_y_cursor_target: int,
    num_seconds: float = None
    ):
    """
    Drag the cursor from current position to specified coordinates on the screen.

    Args:
        coordinate_x_cursor_target (int): The x-coordinate to drag the cursor to
        coordinate_y_cursor_target (int): The y-coordinate to drag the cursor to 
        num_seconds (float, optional): Duration of drag movement in seconds. If None, drags instantly

    Raises:
        ValueError: If target coordinates are outside screen boundaries
    """
    if not pyautogui.onScreen(coordinate_x_cursor_target, coordinate_y_cursor_target):
        raise ValueError("Target coordinates are outside the screen boundaries.")
    try:
        pyautogui.dragTo(coordinate_x_cursor_target, coordinate_y_cursor_target, duration=num_seconds)
        print(f"drag cursor to {coordinate_x_cursor_target}, {coordinate_y_cursor_target}")
        return ShowScreen()
    except Exception as e:
        return f"Error - Failed to drag cursor: {e}"
            
@tool
def KeyboardWriteViaSingleString(text_string: str):
    """
    Write text to the screen using keyboard keys.

    Args:
        text_string (str): Text string to be written
        secs_between_keys (float): Delay between key presses in seconds

    Returns:
        None

    Raises:
        ValueError: If text_string is empty
    """
    if not text_string:
        raise ValueError("Text string cannot be empty.")
    try:
        pyautogui.write(text_string, interval=0.5)
        print(f"Write success {text_string}")
        return ShowScreen()
    except Exception as e:
        return f"Error - Failed to write text: {e}"
           
# @tool 
# def KeyboardWriteViaListString(list_of_text_string: List[str]):
#     """
#     Write a list of text strings to the screen using keyboard keys.

#     Args:
#         list_of_text_string (List[str]): List of text strings to be written
#         secs_between_keys (float): Delay between key presses in seconds

#     Returns:
#         None

#     Raises:
#         ValueError: If list_of_text_string is empty
#     """
#     if not list_of_text_string:
#         raise ValueError("Text string cannot be empty.")
#     try:
#         pyautogui.write(list_of_text_string, interval=0.5)
#         print(f"Write success {list_of_text_string}")
#         return ShowScreen()
#     except Exception as e:
#         return f"Error - Failed to write text: {e}"
    
@tool
def KeyboardHotkey(*hotkey: str):
    """
    Simulate keyboard hotkey press.

    Args:
        hotkey (str): Hotkey to be pressed. Pass multiple keys as separate arguments.
        
    Examples:
        # Press Ctrl+C to copy
        KeyboardHotkey('ctrl', 'c')
        
        # Press Ctrl+Alt+Delete
        KeyboardHotkey('ctrl', 'alt', 'delete')
        
        # Press Windows+D to show desktop
        KeyboardHotkey('win', 'd')
        
        # Press Alt+Tab to switch windows
        KeyboardHotkey('alt', 'tab')

    Returns:
        None

    Raises:
        ValueError: If hotkey is empty
    """
    if not hotkey:
        raise ValueError("Hotkey cannot be empty.")
    try:
        pyautogui.hotkey(hotkey)
        print(f"Write success {hotkey}")
        return ShowScreen()
    except Exception as e:
        return f"Error - Failed to press hotkey: {e}"
    
ToolBox = [
    ShowScreen, 
    CursorMove,
    CursorMoveAndClick,
    CursorDrag,
    KeyboardWriteViaSingleString,
    # KeyboardWriteViaListString,
    KeyboardHotkey
]
