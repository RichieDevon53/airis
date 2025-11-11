from PIL import ImageGrab

def screenshot() -> None:
    screenshot = ImageGrab.grab()
    screenshot.save("temp\\temp.png")
    
def gettemp() -> str:
    return "temp\\temp.png"
