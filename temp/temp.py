from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import math

# --- STYLE CONFIGURATION ---
# Centralized configuration for easy visual adjustments.
STYLE_CONFIG = {
    "colors": {
        "background_dim": (10, 20, 30, 190),  # Dark navy dimming layer
        "highlight_glow": "#FFD700",          # Vibrant gold for glows and highlights
        "text_box_bg": (45, 55, 70, 235),      # Sophisticated charcoal-blue background
        "text_box_shadow": (0, 0, 0, 100),    # Soft black for drop shadows
        "text_primary": "#F5F5F5",             # Soft off-white for better readability
        "text_title": "#FFFFFF",               # Pure white for main titles
        "text_shadow": (0, 0, 0, 128),         # Dark shadow for text
    },
    "fonts": {
        "title": ["fonts/Roboto-Bold.ttf", "arialbd.ttf"], # Primary, fallback
        "body": ["fonts/Roboto-Regular.ttf", "arial.ttf"], # Primary, fallback
        "title_size": 32,
        "body_size": 26,
    },
    "dimensions": {
        "corner_radius": 12,
        "highlight_width": 3,
        "glow_radius": 15,
        "shadow_offset": (8, 8),
        "shadow_blur_radius": 10,
        "arrow_width": 4,
        "arrowhead_length": 25,
        "arrowhead_angle": 30,
    },
}

# --- HELPER FUNCTIONS ---

def get_font(font_names, size):
    """Attempts to load a preferred font, with fallbacks."""
    for font_name in font_names:
        try:
            return ImageFont.truetype(font_name, size)
        except IOError:
            continue
    print(f"Warning: Could not load preferred fonts {font_names}. Falling back to default.")
    return ImageFont.load_default()

def draw_rounded_rectangle(draw, xy, radius, **kwargs):
    """Draws a rectangle with rounded corners."""
    x1, y1, x2, y2 = xy
    draw.rectangle(
        (x1 + radius, y1, x2 - radius, y2),
        **kwargs
    )
    draw.rectangle(
        (x1, y1 + radius, x2, y2 - radius),
        **kwargs
    )
    draw.pieslice(
        (x1, y1, x1 + radius * 2, y1 + radius * 2),
        180, 270, **kwargs
    )
    draw.pieslice(
        (x2 - radius * 2, y1, x2, y1 + radius * 2),
        270, 360, **kwargs
    )
    draw.pieslice(
        (x1, y2 - radius * 2, x1 + radius * 2, y2),
        90, 180, **kwargs
    )
    draw.pieslice(
        (x2 - radius * 2, y2 - radius * 2, x2, y2),
        0, 90, **kwargs
    )

def draw_text_with_shadow(draw, pos, text, font, fill_color, shadow_color, offset=(2, 2)):
    """Draws text with a subtle drop shadow for better readability."""
    shadow_pos = (pos[0] + offset[0], pos[1] + offset[1])
    draw.text(shadow_pos, text, font=font, fill=shadow_color)
    draw.text(pos, text, font=font, fill=fill_color)

def draw_elegant_arrow(draw, start, end, color, width, head_length, head_angle):
    """Draws a line with a sleek, open-style chevron arrowhead."""
    # Draw the main line
    draw.line([start, end], fill=color, width=width)

    # Calculate arrowhead geometry
    angle = math.atan2(start[1] - end[1], start[0] - end[0])
    angle1 = angle + math.radians(head_angle)
    angle2 = angle - math.radians(head_angle)

    # Points for the two lines of the arrowhead
    p1 = (end[0] + head_length * math.cos(angle1), end[1] + head_length * math.sin(angle1))
    p2 = (end[0] + head_length * math.cos(angle2), end[1] + head_length * math.sin(angle2))

    draw.line([end, p1], fill=color, width=width)
    draw.line([end, p2], fill=color, width=width)

def create_youtube_share_overlay():
    """
    Creates a professionally designed Pillow (PIL) overlay to explain the YouTube share button.
    """
    # Define the exact canvas size (PRESERVED)
    width, height = 1920, 1080
    size = (width, height)

    # Path to the original screenshot
    screenshot_path = "screenshot.png"
    
    # Create a temporary directory if it doesn't exist
    if not os.path.exists("temp"):
        os.makedirs("temp")

    # Load the background screenshot
    try:
        background = Image.open(screenshot_path).convert("RGBA").resize(size)
    except FileNotFoundError:
        background = Image.new("RGBA", size, (255, 255, 255, 255))
        draw_bg = ImageDraw.Draw(background)
        draw_bg.text((50, 50), "Screenshot not found. This is a dummy background.", fill="black")

    # Create the overlay image with a transparent background
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    
    # Add a semi-transparent dark layer for better contrast
    draw = ImageDraw.Draw(overlay)
    draw.rectangle([(0, 0), size], fill=STYLE_CONFIG["colors"]["background_dim"])

    # --- Annotation Details ---

    # Load fonts using the helper function for robust loading
    font_title = get_font(STYLE_CONFIG["fonts"]["title"], STYLE_CONFIG["fonts"]["title_size"])
    font_body = get_font(STYLE_CONFIG["fonts"]["body"], STYLE_CONFIG["fonts"]["body_size"])

    # 1. Highlight the "Bagikan" (Share) button with a glow effect
    # Coordinates are PRESERVED from the original code
    button_coords = (430, 865, 530, 905)
    
    # Create a temporary layer for the glow effect
    glow_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    
    # Draw the shape to be blurred for the glow
    draw_rounded_rectangle(
        glow_draw, button_coords, 
        radius=STYLE_CONFIG["dimensions"]["corner_radius"],
        fill=STYLE_CONFIG["colors"]["highlight_glow"]
    )
    
    # Apply Gaussian blur to create the glow
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(STYLE_CONFIG["dimensions"]["glow_radius"]))
    
    # Composite the glow onto the main overlay
    overlay.paste(glow_layer, (0, 0), glow_layer)
    
    # Draw a crisp outline on top of the glow
    draw_rounded_rectangle(
        draw, button_coords,
        radius=STYLE_CONFIG["dimensions"]["corner_radius"],
        outline=STYLE_CONFIG["colors"]["highlight_glow"],
        width=STYLE_CONFIG["dimensions"]["highlight_width"]
    )

    # 2. Create the explanatory text box
    # Positioning logic is PRESERVED
    text_box_start = (550, 800)
    line1 = "Tombol Bagikan (Share)"
    line2 = "Klik di sini untuk menyalin tautan (link) video atau"
    line3 = "membagikannya ke platform lain seperti media sosial."

    # Calculate text dimensions (PRESERVED LOGIC)
    line1_bbox = draw.textbbox((0,0), line1, font=font_title)
    line2_bbox = draw.textbbox((0,0), line2, font=font_body)
    line3_bbox = draw.textbbox((0,0), line3, font=font_body)
    
    text_width = max(line1_bbox[2], line2_bbox[2], line3_bbox[2])
    text_height = (line1_bbox[3] + line2_bbox[3] + line3_bbox[3] + 40)
    
    text_bg_coords = [
        text_box_start[0], 
        text_box_start[1], 
        text_box_start[0] + text_width + 40,
        text_box_start[1] + text_height
    ]

    # Draw a soft drop shadow for the text box
    shadow_offset = STYLE_CONFIG["dimensions"]["shadow_offset"]
    shadow_coords = [
        text_bg_coords[0] + shadow_offset[0],
        text_bg_coords[1] + shadow_offset[1],
        text_bg_coords[2] + shadow_offset[0],
        text_bg_coords[3] + shadow_offset[1]
    ]
    shadow_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    draw_rounded_rectangle(shadow_draw, shadow_coords, radius=STYLE_CONFIG["dimensions"]["corner_radius"], fill=STYLE_CONFIG["colors"]["text_box_shadow"])
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(STYLE_CONFIG["dimensions"]["shadow_blur_radius"]))
    overlay.paste(shadow_layer, (0,0), shadow_layer)

    # Draw the main rounded rectangle for the text background
    draw_rounded_rectangle(draw, text_bg_coords, radius=STYLE_CONFIG["dimensions"]["corner_radius"], fill=STYLE_CONFIG["colors"]["text_box_bg"])
    
    # Draw the text with shadows for improved readability
    current_y = text_box_start[1] + 15
    draw_text_with_shadow(draw, (text_box_start[0] + 20, current_y), line1, font_title, STYLE_CONFIG["colors"]["text_title"], STYLE_CONFIG["colors"]["text_shadow"])
    current_y += line1_bbox[3] + 15
    draw_text_with_shadow(draw, (text_box_start[0] + 20, current_y), line2, font_body, STYLE_CONFIG["colors"]["text_primary"], STYLE_CONFIG["colors"]["text_shadow"])
    current_y += line2_bbox[3] + 5
    draw_text_with_shadow(draw, (text_box_start[0] + 20, current_y), line3, font_body, STYLE_CONFIG["colors"]["text_primary"], STYLE_CONFIG["colors"]["text_shadow"])

    # 3. Draw an elegant arrow pointing from the text box to the highlighted button
    # Arrow coordinate logic is PRESERVED
    arrow_start = (text_bg_coords[0], text_box_start[1] + text_height / 2)
    arrow_end = (button_coords[2] + 5, button_coords[1] + (button_coords[3] - button_coords[1]) / 2)
    draw_elegant_arrow(
        draw, arrow_start, arrow_end,
        color=STYLE_CONFIG["colors"]["highlight_glow"],
        width=STYLE_CONFIG["dimensions"]["arrow_width"],
        head_length=STYLE_CONFIG["dimensions"]["arrowhead_length"],
        head_angle=STYLE_CONFIG["dimensions"]["arrowhead_angle"]
    )

    # Composite the background with the final overlay (PRESERVED)
    final_image = Image.alpha_composite(background, overlay)

    # Save the final image (PRESERVED)
    output_path = "temp/overlay.png"
    final_image.save(output_path)
    print(f"Enhanced overlay saved to {output_path}")

    # Display the image
    final_image.show()

if __name__ == "__main__":
    # Note: For best results, download the Roboto font from Google Fonts
    # and place 'Roboto-Bold.ttf' and 'Roboto-Regular.ttf' in a 'fonts' sub-directory.
    # The code will fall back to Arial if they are not found.
    if not os.path.exists("fonts"):
        print("Info: 'fonts' directory not found. Consider creating it and adding Roboto fonts for the best visual quality.")
    create_youtube_share_overlay()
