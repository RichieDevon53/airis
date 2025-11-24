from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# =============================================================================
# 1. PROFESSIONAL STYLE CONFIGURATION
# Centralized styling for easy theme modification.
# =============================================================================
class Style:
    """A class to hold all styling constants for the overlay."""
    # --- Color Palette ---
    # A modern, high-contrast palette.
    PALETTE = {
        "background_tint": (10, 20, 40, 120),    # Deep semi-transparent navy
        "primary_highlight": (255, 190, 0, 255),  # Vibrant, warm gold
        "glow_color": (255, 210, 80, 255),     # Softer gold for the glow effect
        "text_primary": (240, 240, 245, 255),    # Soft off-white
        "shadow_dark": (0, 0, 0, 150),          # Soft, transparent black for shadows
        "title_background": (20, 30, 55, 230),   # Darker navy for title backdrop
    }

    # --- Typography ---
    # Prioritizes modern fonts with fallbacks.
    FONT_PATHS = ["seguisb.ttf", "arialbd.ttf"] # Try Segoe UI Semibold, then Arial Bold
    TITLE_FONT_SIZE = 56
    
    # --- Shape & Effects Styling ---
    UPSCALE_FACTOR = 2  # For anti-aliasing; draw at 2x resolution then downscale.
    CIRCLE_WIDTH = 4
    CIRCLE_GLOW_LAYERS = 3
    TITLE_RECT_RADIUS = 20
    SHADOW_OFFSET = (4, 4)

# =============================================================================
# 2. HELPER FUNCTIONS FOR ADVANCED DRAWING
# Encapsulated logic for creating professional visual effects.
# =============================================================================

def load_font(preferred_fonts, size):
    """Attempts to load a font from a list of preferred paths, with a fallback."""
    for font_name in preferred_fonts:
        try:
            return ImageFont.truetype(font_name, size)
        except IOError:
            continue
    print(f"Warning: Preferred fonts not found. Falling back to default.")
    return ImageFont.load_default()

def draw_text_with_shadow(draw, pos, text, font, fill_color, shadow_color, offset, anchor="lt"):
    """Draws text with a subtle drop shadow for better readability."""
    shadow_pos = (pos[0] + offset[0], pos[1] + offset[1])
    draw.text(shadow_pos, text, font=font, fill=shadow_color, anchor=anchor)
    draw.text(pos, text, font=font, fill=fill_color, anchor=anchor)

def draw_glowing_ellipse(draw, xy, color, glow_color, width, glow_layers):
    """Draws an ellipse with a soft outer glow."""
    # CRITICAL: Preserve original coordinate values for the main shape
    original_xy = xy
    
    # Draw glow layers first, from largest and most transparent to smallest
    for i in range(glow_layers, 0, -1):
        glow_width = width + i * 2
        # Use an alpha that decreases with distance for a soft falloff
        glow_alpha = int(70 / (i + 1)) 
        current_glow_color = glow_color[:3] + (glow_alpha,)
        
        # Expand the bounding box for the glow effect
        glow_xy = [
            (xy[0][0] - i*2, xy[0][1] - i*2),
            (xy[1][0] + i*2, xy[1][1] + i*2)
        ]
        draw.ellipse(glow_xy, outline=current_glow_color, width=glow_width)
        
    # Draw the main, sharp ellipse on top
    draw.ellipse(original_xy, outline=color, width=width)

# =============================================================================
# 3. MAIN OVERLAY CREATION FUNCTION
# Integrates styling and helpers to produce the final polished overlay.
# =============================================================================

def create_spot_the_difference_overlay():
    """
    Creates a professionally designed Pillow overlay to highlight 5 differences.
    """
    # --- Canvas Setup (PRESERVED) ---
    width, height = 1920, 1080
    
    # Create the final transparent overlay
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    # Add the semi-transparent background tint directly to the final overlay
    # This ensures it's behind the anti-aliased elements.
    draw_base = ImageDraw.Draw(overlay)
    draw_base.rectangle([0, 0, width, height], fill=Style.PALETTE["background_tint"])

    # --- Anti-Aliasing Setup ---
    # Create an upscaled canvas for drawing high-quality shapes
    UPSCALE = Style.UPSCALE_FACTOR
    up_width, up_height = width * UPSCALE, height * UPSCALE
    hd_canvas = Image.new('RGBA', (up_width, up_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(hd_canvas)

    # --- Title and Header ---
    title_font = load_font(Style.FONT_PATHS, Style.TITLE_FONT_SIZE * UPSCALE)
    title_text = "Here are the 5 differences!"
    
    # Calculate title position (using original dimensions for logic PRESERVATION)
    temp_draw = ImageDraw.Draw(Image.new('RGBA', (1,1))) # Dummy draw for textbbox
    title_bbox = temp_draw.textbbox((0, 0), title_text, font=load_font(Style.FONT_PATHS, Style.TITLE_FONT_SIZE))
    
    title_w = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]
    title_x = (width - title_w) / 2
    title_y = 70
    
    # Define coordinates for the rounded rectangle background (upscaled)
    padding = 20
    rect_x1 = (title_x - padding) * UPSCALE
    rect_y1 = (title_y - padding) * UPSCALE
    rect_x2 = (title_x + title_w + padding) * UPSCALE
    rect_y2 = (title_y + title_h + padding) * UPSCALE
    
    # Draw the shadow for the title box
    shadow_offset_up = (Style.SHADOW_OFFSET[0] * UPSCALE, Style.SHADOW_OFFSET[1] * UPSCALE)
    draw.rounded_rectangle(
        (rect_x1 + shadow_offset_up[0], rect_y1 + shadow_offset_up[1], rect_x2 + shadow_offset_up[0], rect_y2 + shadow_offset_up[1]),
        radius=Style.TITLE_RECT_RADIUS * UPSCALE,
        fill=Style.PALETTE["shadow_dark"]
    )
    # Draw the main title box
    draw.rounded_rectangle(
        (rect_x1, rect_y1, rect_x2, rect_y2),
        radius=Style.TITLE_RECT_RADIUS * UPSCALE,
        fill=Style.PALETTE["title_background"]
    )
    
    # Draw the title text with its shadow
    draw_text_with_shadow(
        draw,
        (width / 2 * UPSCALE, title_y * UPSCALE),
        title_text,
        font=title_font,
        fill_color=Style.PALETTE["text_primary"],
        shadow_color=Style.PALETTE["shadow_dark"],
        offset=shadow_offset_up,
        anchor="mt"
    )

    # --- Highlight Differences with Glowing Circles ---
    # Define circle style from the configuration
    circle_outline_color = Style.PALETTE["primary_highlight"]
    circle_glow_color = Style.PALETTE["glow_color"]
    circle_width = Style.CIRCLE_WIDTH * UPSCALE

    # Define coordinates for the 5 differences (PRESERVED)
    # The coordinates are multiplied by the upscale factor just before drawing.
    diff_coords = [
        [(465, 315), (505, 355)],  # 1. Worm on the roof
        [(1135, 315), (1185, 355)], # 2. Butterfly in the sky
        [(1205, 535), (1245, 575)], # 3. Pattern on the window
        [(625, 625), (680, 675)],  # 4. Purple mushrooms
        [(445, 685), (475, 715)],  # 5. White pebble on grass
    ]

    for coords in diff_coords:
        # Upscale coordinates for high-resolution drawing
        upscaled_coords = [
            (coords[0][0] * UPSCALE, coords[0][1] * UPSCALE),
            (coords[1][0] * UPSCALE, coords[1][1] * UPSCALE)
        ]
        draw_glowing_ellipse(
            draw, 
            upscaled_coords, 
            circle_outline_color,
            circle_glow_color,
            circle_width, 
            Style.CIRCLE_GLOW_LAYERS
        )

    # --- Final Composition ---
    # Downscale the high-resolution canvas to the original size with anti-aliasing
    final_elements = hd_canvas.resize((width, height), Image.Resampling.LANCZOS)
    
    # Composite the anti-aliased elements over the base background
    overlay.alpha_composite(final_elements, (0, 0))
    
    # --- Save the Overlay (PRESERVED) ---
    if not os.path.exists('temp'):
        os.makedirs('temp')
    overlay_path = "temp/overlay.png"
    overlay.save(overlay_path)
    print(f"Professionally enhanced overlay saved to {overlay_path}")

# Run the function to create the overlay
if __name__ == "__main__":
    create_spot_the_difference_overlay()
