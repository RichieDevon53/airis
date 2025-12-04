import os
from PIL import Image, ImageDraw, ImageFont

# =============================================================================
# == Professional Style Configuration
# =============================================================================
# By centralizing style properties, we can easily theme the overlay and ensure
# consistency across all visual elements.

STYLE_CONFIG = {
    # --- Color Palette ---
    # A harmonious palette with a deep navy, vibrant gold, and clean off-white
    # for a professional and accessible look.
    "colors": {
        "background_dim": (27, 38, 59, 128),  # Deep semi-transparent navy
        "highlight_primary": (255, 215, 0, 255),  # Vibrant gold (Opaque)
        "highlight_glow": (255, 225, 80, 100),  # Lighter gold (Semi-transparent for glow)
        "text_primary": (240, 240, 245, 255),  # Soft off-white
        "text_shadow": (10, 15, 25, 128),     # Subtle dark shadow
        "title_background": (20, 30, 48, 220),   # Darker, more opaque navy
    },
    
    # --- Typography ---
    # Specifies preferred modern fonts with fallbacks for cross-platform compatibility.
    "typography": {
        "preferred_fonts": ["Verdana.ttf", "Arial.ttf"], # Common sans-serif fonts
        "font_size": 42,
        "text_shadow_offset": (2, 2),
    },

    # --- Shapes & Borders ---
    # Defines properties for drawing shapes, ensuring a consistent aesthetic.
    "shapes": {
        "circle_width": 4,          # Width of the main highlight circle
        "glow_multiplier": 3,       # Multiplier for the glow effect width
        "title_box_padding": 15,    # Padding around the title text
        "title_box_radius": 12,     # Corner radius for the title background
    },
}

# =============================================================================
# == Helper Functions
# =============================================================================

def find_font(preferred_list, size):
    """
    Searches for a font from a preferred list and falls back to a default.
    This improves cross-platform compatibility.
    
    Args:
        preferred_list (list): A list of font file names to search for.
        size (int): The desired font size.

    Returns:
        ImageFont: A Pillow font object.
    """
    for font_name in preferred_list:
        try:
            return ImageFont.truetype(font_name, size)
        except IOError:
            continue  # Font not found, try the next one
    
    print(f"Warning: None of the preferred fonts {preferred_list} were found. "
          "Falling back to the default PIL font.")
    # The default font is very small, so we use a larger size for it if needed
    try:
        # load_default() in newer Pillow versions can take a size argument
        return ImageFont.load_default(size=size//2)
    except TypeError:
        return ImageFont.load_default()


def draw_glow_ellipse(draw_context, xy, primary_color, glow_color, width, glow_multiplier):
    """
    Draws an ellipse with a professional-looking outer glow effect.
    This is achieved by drawing a wider, semi-transparent ellipse behind the main one.

    Args:
        draw_context (ImageDraw): The Pillow drawing context.
        xy (tuple): The bounding box for the ellipse.
        primary_color (tuple): The color of the main outline.
        glow_color (tuple): The color of the outer glow.
        width (int): The width of the main outline.
        glow_multiplier (float): How much wider the glow outline should be.
    """
    # 1. Draw the outer glow: wider and more transparent
    glow_width = int(width * glow_multiplier)
    draw_context.ellipse(xy, outline=glow_color, width=glow_width)
    
    # 2. Draw the main highlight circle on top: sharper and more opaque
    draw_context.ellipse(xy, outline=primary_color, width=width)

# =============================================================================
# == Main Drawing Function
# =============================================================================

def create_spot_the_difference_overlay():
    """
    Creates a professionally styled Pillow (PIL) overlay to highlight the 5 
    differences in the provided screenshot.
    """
    # --- Canvas Definition (PRESERVED) ---
    canvas_width = 1920
    canvas_height = 1080
    canvas_size = (canvas_width, canvas_height)

    # Create a new transparent image for the overlay.
    # Using 'LANCZOS' resampling on a larger canvas and then resizing can
    # produce smoother anti-aliasing, but for simplicity and performance,
    # we will draw directly on the final canvas size.
    overlay = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # --- Difference Coordinates (PRESERVED) ---
    # These coordinates are unchanged as per requirements.
    diff1_coords = (435, 305, 485, 355)
    diff2_coords = (1020, 295, 1070, 345)
    diff3_coords = (418, 535, 458, 575)
    diff4_coords = (610, 565, 660, 615)
    diff5_coords = (575, 650, 605, 680)
    differences = [diff1_coords, diff2_coords, diff3_coords, diff4_coords, diff5_coords]
    
    # --- Drawing Annotations ---

    # 1. Apply a stylish background dim to enhance focus
    draw.rectangle([(0, 0), canvas_size], fill=STYLE_CONFIG["colors"]["background_dim"])

    # 2. Draw a glowing circle around each difference
    for coords in differences:
        draw_glow_ellipse(
            draw_context=draw,
            xy=coords,
            primary_color=STYLE_CONFIG["colors"]["highlight_primary"],
            glow_color=STYLE_CONFIG["colors"]["highlight_glow"],
            width=STYLE_CONFIG["shapes"]["circle_width"],
            glow_multiplier=STYLE_CONFIG["shapes"]["glow_multiplier"]
        )

    # --- Adding Enhanced Explanatory Text ---
    
    # 3. Load a professional font with a fallback mechanism
    font = find_font(
        preferred_list=STYLE_CONFIG["typography"]["preferred_fonts"],
        size=STYLE_CONFIG["typography"]["font_size"]
    )

    # 4. Prepare text and its position (PRESERVED)
    title_text = "Here are the 5 differences:"
    text_position = (760, 180)
    
    # 5. Create a modern, rounded background for the text
    text_bbox = draw.textbbox(text_position, title_text, font=font)
    padding = STYLE_CONFIG["shapes"]["title_box_padding"]
    radius = STYLE_CONFIG["shapes"]["title_box_radius"]
    
    bg_bbox = (
        text_bbox[0] - padding,
        text_bbox[1] - padding,
        text_bbox[2] + padding,
        text_bbox[3] + padding
    )
    
    draw.rounded_rectangle(
        bg_bbox,
        radius=radius,
        fill=STYLE_CONFIG["colors"]["title_background"]
    )

    # 6. Draw text with a subtle shadow for improved readability and depth
    shadow_offset = STYLE_CONFIG["typography"]["text_shadow_offset"]
    shadow_pos = (text_position[0] + shadow_offset[0], text_position[1] + shadow_offset[1])
    
    draw.text(
        shadow_pos,
        title_text,
        fill=STYLE_CONFIG["colors"]["text_shadow"],
        font=font
    )
    draw.text(
        text_position,
        title_text,
        fill=STYLE_CONFIG["colors"]["text_primary"],
        font=font
    )

    # --- Save the Overlay (PRESERVED) ---
    if not os.path.exists('temp'):
        os.makedirs('temp')

    overlay.save("temp/overlay.png")
    print(f"Enhanced overlay saved to temp/overlay.png")

# Run the function to generate the professional overlay
if __name__ == "__main__":
    create_spot_the_difference_overlay()
