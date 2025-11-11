from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageFilter
import os
from math import sin, cos, pi

# Define a professional color palette
COLORS = {
    'primary': (41, 128, 185, 255),       # Blue
    'secondary': (231, 76, 60, 255),      # Red
    'accent': (241, 196, 15, 255),        # Yellow
    'dark': (44, 62, 80, 220),            # Dark blue with transparency
    'light': (236, 240, 241, 255),        # Light gray
    'text_light': (255, 255, 255, 255),   # White
    'text_shadow': (0, 0, 0, 100)         # Semi-transparent black
}

# Create a new transparent overlay with the exact dimensions
overlay = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

# Load fonts with error handling and fallbacks
try:
    title_font = ImageFont.truetype("arial.ttf", 36)
    text_font = ImageFont.truetype("arial.ttf", 24)
    subtitle_font = ImageFont.truetype("arial.ttf", 28)
except:
    print("Warning: Default fonts used due to missing font files")
    title_font = ImageFont.load_default()
    text_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()

# Spain is located in southwestern Europe
# Based on the map in the screenshot, Spain is in Europe
# Approximate coordinates on this specific map (preserving original values)
spain_x, spain_y = 730, 450  # Center point of Spain on this map

# Helper function to create a rounded rectangle
def rounded_rectangle(draw, bbox, radius, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = bbox
    # Draw the main rectangle
    draw.rectangle((x1+radius, y1, x2-radius, y2), fill=fill, outline=None)
    draw.rectangle((x1, y1+radius, x2, y2-radius), fill=fill, outline=None)
    # Draw the four corner circles
    draw.ellipse((x1, y1, x1+radius*2, y1+radius*2), fill=fill, outline=None)
    draw.ellipse((x2-radius*2, y1, x2, y1+radius*2), fill=fill, outline=None)
    draw.ellipse((x1, y2-radius*2, x1+radius*2, y2), fill=fill, outline=None)
    draw.ellipse((x2-radius*2, y2-radius*2, x2, y2), fill=fill, outline=None)
    # Draw outline if specified
    if outline and width > 0:
        draw.arc((x1, y1, x1+radius*2, y1+radius*2), 180, 270, outline=outline, width=width)
        draw.arc((x2-radius*2, y1, x2, y1+radius*2), 270, 360, outline=outline, width=width)
        draw.arc((x1, y2-radius*2, x1+radius*2, y2), 90, 180, outline=outline, width=width)
        draw.arc((x2-radius*2, y2-radius*2, x2, y2), 0, 90, outline=outline, width=width)
        draw.line((x1+radius, y1, x2-radius, y1), fill=outline, width=width)
        draw.line((x1+radius, y2, x2-radius, y2), fill=outline, width=width)
        draw.line((x1, y1+radius, x1, y2-radius), fill=outline, width=width)
        draw.line((x2, y1+radius, x2, y2-radius), fill=outline, width=width)

# Helper function to draw a professional arrow
def draw_arrow(draw, start, end, color, width=5, head_length=20):
    # Draw the line
    draw.line((start[0], start[1], end[0], end[1]), fill=color, width=width)
    
    # Calculate the arrow head
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = (dx**2 + dy**2)**0.5
    dx, dy = dx/length, dy/length
    
    # Calculate perpendicular direction for arrow head
    perpx, perpy = -dy, dx
    
    # Draw arrow head
    arrow_points = [
        (end[0], end[1]),
        (end[0] - head_length*dx + head_length*0.5*perpx, 
         end[1] - head_length*dy + head_length*0.5*perpy),
        (end[0] - head_length*dx - head_length*0.5*perpx, 
         end[1] - head_length*dy - head_length*0.5*perpy)
    ]
    draw.polygon(arrow_points, fill=color)

# Create a glow effect for the highlight circle
glow_overlay = Image.new('RGBA', overlay.size, (0, 0, 0, 0))
glow_draw = ImageDraw.Draw(glow_overlay)
glow_radius = 60
for i in range(10, 0, -1):
    alpha = int(15 * (1 - (i / 10)))
    glow_color = (*COLORS['secondary'][:3], alpha)
    glow_draw.ellipse(
        (spain_x-glow_radius-i, spain_y-glow_radius-i, 
         spain_x+glow_radius+i, spain_y+glow_radius+i), 
        fill=None, outline=glow_color, width=2
    )
glow_overlay = glow_overlay.filter(ImageFilter.GaussianBlur(10))
overlay = Image.alpha_composite(overlay, glow_overlay)
draw = ImageDraw.Draw(overlay)

# Draw a professional highlight circle around Spain
draw.ellipse(
    (spain_x-50, spain_y-40, spain_x+50, spain_y+40), 
    outline=COLORS['secondary'], width=5
)

# Add a pulsing inner circle for emphasis
inner_circle_radius = 30
draw.ellipse(
    (spain_x-inner_circle_radius, spain_y-inner_circle_radius, 
     spain_x+inner_circle_radius, spain_y+inner_circle_radius), 
    outline=COLORS['accent'], width=2
)

# Add an arrow pointing to Spain with improved styling
arrow_start_x, arrow_start_y = 850, 350
draw_arrow(
    draw, 
    (arrow_start_x, arrow_start_y), 
    (spain_x+10, spain_y-10), 
    COLORS['secondary'], 
    width=4
)

# Add explanatory text with professional background
text = "SPAIN"
text_position = (arrow_start_x + 10, arrow_start_y - 40)
text_bbox = draw.textbbox(text_position, text, font=title_font)

# Create a professional text background with rounded corners
text_bg_bbox = (
    text_bbox[0]-20, text_bbox[1]-15, 
    text_bbox[2]+20, text_bbox[3]+10
)
rounded_rectangle(
    draw, text_bg_bbox, 10, 
    fill=COLORS['dark'], 
    outline=(*COLORS['secondary'][:3], 100), 
    width=2
)

# Add text shadow for depth
shadow_offset = 2
draw.text(
    (text_position[0]+shadow_offset, text_position[1]+shadow_offset), 
    text, font=title_font, fill=COLORS['text_shadow']
)
# Draw the main text
draw.text(
    text_position, text, 
    font=title_font, fill=COLORS['text_light']
)

# Add educational information with enhanced styling
info_text = [
    "• Located in southwestern Europe",
    "• Shares the Iberian Peninsula with Portugal",
    "• Bordered by France to the northeast",
    "• Mediterranean Sea to the east and south",
    "• Atlantic Ocean to the northwest"
]

# Create a professional info panel
info_x, info_y = 1000, 400
info_width = 550
info_height = len(info_text) * 35 + 50

# Draw panel background with rounded corners
panel_bbox = (
    info_x - 20, info_y - 40, 
    info_x + info_width, info_y + info_height
)
rounded_rectangle(
    draw, panel_bbox, 15, 
    fill=(*COLORS['dark'][:3], 180), 
    outline=(*COLORS['primary'][:3], 100), 
    width=2
)

# Add panel title
panel_title = "Geographic Context"
draw.text(
    (info_x, info_y - 30), 
    panel_title, 
    font=subtitle_font, 
    fill=COLORS['accent']
)

# Add info text items with subtle styling
for line in info_text:
    draw.text(
        (info_x, info_y), 
        line, 
        font=text_font, 
        fill=COLORS['text_light']
    )
    info_y += 35

# Save the overlay
os.makedirs("temp", exist_ok=True)
overlay.save("temp/overlay.png")

print("Enhanced overlay created and saved to temp/overlay.png")
