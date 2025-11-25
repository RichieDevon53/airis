from PIL import ImageGrab

def screenshot() -> None:
    screenshot = ImageGrab.grab()
    screenshot.save("temp\\temp.png")

def screenshot_history(id: str) -> None:
    screenshot = ImageGrab.grab()
    screenshot.save(f"temp\\history_{id}.png")
    
def gettemp() -> str:
    return "temp\\temp.png"
