from PIL import Image, ImageDraw, ImageFont, ImageFilter
import tkinter as tk
from PIL import ImageTk

# --- Style Constants ---
CANVAS_SIZE = (1920, 1080)

# --- Color Palette (Professional & Accessible) ---
PRIMARY_COLOR = (63, 81, 181, 230)       # Indigo, slightly transparent
SECONDARY_COLOR = (255, 235, 59, 230)    # Yellow, slightly transparent
ACCENT_COLOR = (76, 175, 80, 230)        # Green, slightly transparent
TEXT_COLOR = (33, 33, 33, 255)           # Dark Gray (for readability)
BACKGROUND_COLOR = (255, 255, 255, 235)  # Off-White, slightly transparent
SHADOW_COLOR = (0, 0, 0, 90)             # Semi-transparent black for shadows

# --- Font Styles ---
FONT_NAME = "arial.ttf"  # Modern, readable font
FONT_SIZE_NORMAL = 24
FONT_SIZE_LARGE = 30
FONT_WEIGHT_NORMAL = "normal"
FONT_WEIGHT_BOLD = "bold"

# --- Shape & Border Styles ---
CORNER_RADIUS = 8
BORDER_WIDTH = 2
SHADOW_OFFSET = 3

# --- Utility Functions ---
def draw_rounded_rectangle(draw, x1, y1, x2, y2, radius, fill, outline=None, width=1):
    """Draw a rounded rectangle with given coordinates, radius, fill, and outline."""
    draw.pieslice([(x1, y1), (x1 + radius * 2, y1 + radius * 2)], 180, 270, fill=fill, outline=outline)
    draw.pieslice([(x2 - radius * 2, y1), (x2, y1 + radius * 2)], 270, 0, fill=fill, outline=outline)
    draw.pieslice([(x2 - radius * 2, y2 - radius * 2), (x2, y2)], 0, 90, fill=fill, outline=outline)
    draw.pieslice([(x1, y2 - radius * 2), (x1 + radius * 2, y2)], 90, 180, fill=fill, outline=outline)
    draw.rectangle([(x1 + radius, y1), (x2 - radius, y2)], fill=fill, outline=outline)
    draw.rectangle([(x1, y1 + radius), (x2, y2 - radius)], fill=fill, outline=outline)

# --- Initialize Canvas ---
overlay = Image.new('RGBA', CANVAS_SIZE, (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

# --- Font Loading ---
try:
    font_normal = ImageFont.truetype(FONT_NAME, size=FONT_SIZE_NORMAL)
    font_large = ImageFont.truetype(FONT_NAME, size=FONT_SIZE_LARGE)
except IOError:
    font_normal = ImageFont.load_default()
    font_large = font_normal  # Fallback to default font

# --- Annotations ---
# Improved visual styling for annotations

# Commented lines:
# Line 23: # self.board_chain = BoardChain(self.gen_ai.pixtral())
x, y = 180, 358
# Add shadow
draw_rounded_rectangle(draw, x - SHADOW_OFFSET, y - 10 + SHADOW_OFFSET, x + 600 + SHADOW_OFFSET, y + 20 + SHADOW_OFFSET, CORNER_RADIUS, fill=SHADOW_COLOR)
# Add actual rectangle
draw_rounded_rectangle(draw, x, y - 10, x + 600, y + 20, CORNER_RADIUS, fill=BACKGROUND_COLOR, outline=PRIMARY_COLOR, width=BORDER_WIDTH)
draw.text((x + 8, y), "# self.board_chain = BoardChain(self.gen_ai.pixtral())", fill=TEXT_COLOR, font=font_normal)


# Line 24: # self.board_chain = BoardChain(self.gen_ai.mini4o(max_tokens=16000))
x, y = 180, 393
# Add shadow
draw_rounded_rectangle(draw, x - SHADOW_OFFSET, y - 10 + SHADOW_OFFSET, x + 750 + SHADOW_OFFSET, y + 20 + SHADOW_OFFSET, CORNER_RADIUS, fill=SHADOW_COLOR)
# Add actual rectangle
draw_rounded_rectangle(draw, x, y - 10, x + 750, y + 20, CORNER_RADIUS, fill=BACKGROUND_COLOR, outline=PRIMARY_COLOR, width=BORDER_WIDTH)
draw.text((x + 8, y), "# self.board_chain = BoardChain(self.gen_ai.mini4o(max_tokens=16000))", fill=TEXT_COLOR, font=font_normal)


# Line 25: # self.board_chain = BoardChain(self.llm)
x, y = 180, 428
# Add shadow
draw_rounded_rectangle(draw, x - SHADOW_OFFSET, y - 10 + SHADOW_OFFSET, x + 450 + SHADOW_OFFSET, y + 20 + SHADOW_OFFSET, CORNER_RADIUS, fill=SHADOW_COLOR)
# Add actual rectangle
draw_rounded_rectangle(draw, x, y - 10, x + 450, y + 20, CORNER_RADIUS, fill=BACKGROUND_COLOR, outline=PRIMARY_COLOR, width=BORDER_WIDTH)
draw.text((x + 8, y), "# self.board_chain = BoardChain(self.llm)", fill=TEXT_COLOR, font=font_normal)


# Explanation for the commented lines
text = "These lines are commented out, meaning they won't be executed.  They likely represent alternative implementations or disabled features."
x, y = 180, 470
# Add shadow
draw_rounded_rectangle(draw, x - SHADOW_OFFSET, y - 10 + SHADOW_OFFSET, x + 850 + SHADOW_OFFSET, y + 20 + SHADOW_OFFSET, CORNER_RADIUS, fill=SHADOW_COLOR)
# Add actual rectangle
draw_rounded_rectangle(draw, x, y - 10, x + 850, y + 20, CORNER_RADIUS, fill=BACKGROUND_COLOR, outline=PRIMARY_COLOR, width=BORDER_WIDTH)
draw.text((x + 8, y), text, fill=TEXT_COLOR, font=font_normal)

# --- Save Overlay ---
overlay.save("temp/overlay.png")

# --- Display Overlay (Tkinter) ---
root = tk.Tk()
root.title("Pillow Overlay")
root.geometry(f"{CANVAS_SIZE[0]}x{CANVAS_SIZE[1]}")

img = ImageTk.PhotoImage(Image.open("temp/overlay.png"))
label = tk.Label(root, image=img)
label.pack(fill="both", expand=True)

root.mainloop()
