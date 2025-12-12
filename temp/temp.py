from PIL import Image, ImageDraw, ImageFont
import math
import os

# --- Style Constants ---
class Palette:
    """Defines a professional color palette for the overlay elements."""
    PRIMARY_HIGHLIGHT_FILL = (255, 204, 0, 80)       # Soft gold, translucent fill for highlight
    PRIMARY_HIGHLIGHT_OUTLINE = (255, 204, 0, 220)    # Brighter gold, more opaque outline
    ACCENT_ARROW = (218, 165, 32, 255)              # Saturated gold for arrow
    TEXT_BG = (30, 30, 30, 210)                     # Dark charcoal, translucent for text background
    TEXT_COLOR = (240, 240, 240, 255)               # Off-white text
    SHADOW_COLOR = (0, 0, 0, 70)                    # Soft black for general shadows
    BORDER_COLOR = (60, 60, 60, 150)                # Subtle grey for text box border

class Styles:
    """Defines visual styles and dimensions for overlay elements."""
    # Font settings
    FONT_SIZE = 28
    FONT_NAME = "segoeui.ttf" # Preferred font (Windows). Fallback to Arial.

    # Highlight rectangle settings
    HIGHLIGHT_OUTLINE_WIDTH = 4
    HIGHLIGHT_CORNER_RADIUS = 10
    HIGHLIGHT_SHADOW_OFFSET = (3, 3) # (x, y) offset for shadows

    # Text box settings
    TEXT_PADDING_HORIZONTAL = 12 # Padding left/right of text content
    TEXT_PADDING_VERTICAL = 8    # Padding top/bottom of text content
    TEXT_VERTICAL_GAP_FROM_OBJECT = 20 # Vertical gap between text box and highlighted object
    TEXT_BG_CORNER_RADIUS = 8
    TEXT_SHADOW_OFFSET = (1, 1)  # (x, y) offset for text shadow
    TEXT_SHADOW_COLOR = (0, 0, 0, 150) # Dark, semi-transparent for text shadow
    TEXT_BORDER_WIDTH = 1
    TEXT_BORDER_OUTER_PADDING = 3 # Space between text_bg and its border

    # Arrow settings
    ARROW_WIDTH = 4
    ARROW_HEAD_SIZE = 12
    ARROW_SHADOW_OFFSET = (2, 2) # (x, y) offset for arrow shadow

def create_overlay(screenshot_path, canvas_size=(1920, 1080)):
    """
    Creates a professionally styled Pillow overlay to highlight the gold bars in the screenshot.
    This function preserves all original coordinate calculations and positioning logic,
    while enhancing the visual presentation of elements like rectangles, text boxes, and arrows.

    Args:
        screenshot_path (str): Path to the original screenshot.
        canvas_size (tuple): The target size for the overlay (width, height).
    """
    try:
        # Load the original screenshot to get its dimensions
        original_screenshot = Image.open(screenshot_path)
        original_width, original_height = original_screenshot.size

        # Create a transparent RGBA canvas for the overlay
        overlay = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Calculate scaling factors and letterbox parameters
        scale_x = canvas_size[0] / original_width
        scale_y = canvas_size[1] / original_height

        # Determine if letterboxing is needed to maintain aspect ratio
        target_ratio = canvas_size[0] / canvas_size[1]
        img_ratio = original_width / original_height

        paste_x, paste_y = 0, 0
        resized_img = original_screenshot

        if abs(target_ratio - img_ratio) > 0.05: # If aspect ratios differ significantly
            if img_ratio > target_ratio:
                # Image is wider than canvas, fit by width (letterbox top/bottom)
                new_width = canvas_size[0]
                new_height = int(new_width / img_ratio)
                paste_y = (canvas_size[1] - new_height) // 2
            else:
                # Image is taller than canvas, fit by height (letterbox left/right)
                new_height = canvas_size[1]
                new_width = int(new_height * img_ratio)
                paste_x = (canvas_size[0] - new_width) // 2
            resized_img = original_screenshot.resize((new_width, new_height), Image.LANCZOS)
            # Update scaling factors based on the new dimensions for accurate content placement
            scale_x = new_width / original_width
            scale_y = new_height / original_height

        # Create a translucent version of the background image for context
        translucent_bg = Image.new('RGBA', resized_img.size)
        translucent_bg = Image.alpha_composite(translucent_bg, resized_img.convert('RGBA'))
        draw_bg = ImageDraw.Draw(translucent_bg)
        # Apply a subtle darkening effect to the background for better contrast with overlay elements
        draw_bg.rectangle([(0, 0), resized_img.size], fill=(0, 0, 0, 75))
        overlay.paste(translucent_bg, (paste_x, paste_y), translucent_bg)

        # Load font with fallback mechanisms
        try:
            font = ImageFont.truetype(Styles.FONT_NAME, Styles.FONT_SIZE)
        except IOError:
            print(f"Warning: Font '{Styles.FONT_NAME}' not found. Attempting to use Arial.")
            try:
                font = ImageFont.truetype("arial.ttf", Styles.FONT_SIZE)
            except IOError:
                print("Warning: Arial font not found. Using default Pillow font.")
                font = ImageFont.load_default()

        # --- Manual Annotation for "gold" ---
        # Visually estimated coordinates for the gold bars in the original image.
        # CRITICAL: These original coordinates are preserved.
        gold_bbox_original = [600, 280, 800, 440]

        # Scale and clamp coordinates to ensure they are within the canvas bounds.
        # CRITICAL: Scaling and clamping logic is preserved.
        scaled_x1 = max(0, min(canvas_size[0], int(gold_bbox_original[0] * scale_x + paste_x)))
        scaled_y1 = max(0, min(canvas_size[1], int(gold_bbox_original[1] * scale_y + paste_y)))
        scaled_x2 = max(0, min(canvas_size[0], int(gold_bbox_original[2] * scale_x + paste_x)))
        scaled_y2 = max(0, min(canvas_size[1], int(gold_bbox_original[3] * scale_y + paste_y)))

        # Calculate center of the highlighted object for arrow targeting
        scaled_center_x = (scaled_x1 + scaled_x2) // 2
        scaled_center_y = (scaled_y1 + scaled_y2) // 2

        # --- Draw Highlight Rectangle with Professional Styling ---
        highlight_bbox_coords = [scaled_x1, scaled_y1, scaled_x2, scaled_y2]
        
        # Draw subtle drop shadow for depth
        shadow_bbox = [
            highlight_bbox_coords[0] + Styles.HIGHLIGHT_SHADOW_OFFSET[0],
            highlight_bbox_coords[1] + Styles.HIGHLIGHT_SHADOW_OFFSET[1],
            highlight_bbox_coords[2] + Styles.HIGHLIGHT_SHADOW_OFFSET[0],
            highlight_bbox_coords[3] + Styles.HIGHLIGHT_SHADOW_OFFSET[1]
        ]
        draw.rounded_rectangle(shadow_bbox, radius=Styles.HIGHLIGHT_CORNER_RADIUS, fill=Palette.SHADOW_COLOR)

        # Draw the main highlight rectangle with rounded corners, fill, and a defined outline
        draw.rounded_rectangle(
            highlight_bbox_coords,
            radius=Styles.HIGHLIGHT_CORNER_RADIUS,
            fill=Palette.PRIMARY_HIGHLIGHT_FILL,
            outline=Palette.PRIMARY_HIGHLIGHT_OUTLINE,
            width=Styles.HIGHLIGHT_OUTLINE_WIDTH
        )

        # --- Text Annotation with Professional Background and Shadows ---
        explanation_text = "This image represents gold bars, often used as a symbol of wealth or value."
        
        # Get actual text content dimensions using textbbox for accurate padding
        text_bbox_content = draw.textbbox((0, 0), explanation_text, font=font)
        text_content_width = text_bbox_content[2] - text_bbox_content[0]
        text_content_height = text_bbox_content[3] - text_bbox_content[1]

        # Determine the top-left (x,y) for the *text content* itself.
        # CRITICAL: Original positioning logic for text is preserved.
        text_x = max(10, min(canvas_size[0] - text_content_width - 10, scaled_center_x - text_content_width // 2))
        text_y = scaled_y1 - text_content_height - Styles.TEXT_VERTICAL_GAP_FROM_OBJECT # Gap above object

        # Adjust text position if it goes off the top of the canvas
        if text_y < 10:
            text_y = scaled_y2 + Styles.TEXT_VERTICAL_GAP_FROM_OBJECT # Place below object
            # Ensure text (with full background padding and border) doesn't go off bottom
            if text_y + text_content_height + Styles.TEXT_PADDING_VERTICAL * 2 + Styles.TEXT_BORDER_OUTER_PADDING * 2 > canvas_size[1] - 10:
                text_y = canvas_size[1] - (text_content_height + Styles.TEXT_PADDING_VERTICAL * 2 + Styles.TEXT_BORDER_OUTER_PADDING * 2) - 10

        # Calculate coordinates for the text background rectangle (including inner padding)
        text_bg_x1 = text_x - Styles.TEXT_PADDING_HORIZONTAL
        text_bg_y1 = text_y - Styles.TEXT_PADDING_VERTICAL
        text_bg_x2 = text_x + text_content_width + Styles.TEXT_PADDING_HORIZONTAL
        text_bg_y2 = text_y + text_content_height + Styles.TEXT_PADDING_VERTICAL
        text_bg_bbox = [text_bg_x1, text_bg_y1, text_bg_x2, text_bg_y2]

        # Draw text background shadow
        shadow_bg_bbox = [
            text_bg_bbox[0] + Styles.HIGHLIGHT_SHADOW_OFFSET[0],
            text_bg_bbox[1] + Styles.HIGHLIGHT_SHADOW_OFFSET[1],
            text_bg_bbox[2] + Styles.HIGHLIGHT_SHADOW_OFFSET[0],
            text_bg_bbox[3] + Styles.HIGHLIGHT_SHADOW_OFFSET[1]
        ]
        draw.rounded_rectangle(shadow_bg_bbox, radius=Styles.TEXT_BG_CORNER_RADIUS, fill=Palette.SHADOW_COLOR)

        # Draw the main text background with rounded corners
        draw.rounded_rectangle(text_bg_bbox, radius=Styles.TEXT_BG_CORNER_RADIUS, fill=Palette.TEXT_BG)

        # Calculate coordinates for the text box border (outermost visual element of the text box)
        border_x1 = text_bg_x1 - Styles.TEXT_BORDER_OUTER_PADDING
        border_y1 = text_bg_y1 - Styles.TEXT_BORDER_OUTER_PADDING
        border_x2 = text_bg_x2 + Styles.TEXT_BORDER_OUTER_PADDING
        border_y2 = text_bg_y2 + Styles.TEXT_BORDER_OUTER_PADDING
        
        # Draw a subtle border around the text background
        draw.rounded_rectangle(
            [border_x1, border_y1, border_x2, border_y2],
            radius=Styles.TEXT_BG_CORNER_RADIUS + Styles.TEXT_BORDER_OUTER_PADDING, # Larger radius for border
            outline=Palette.BORDER_COLOR,
            width=Styles.TEXT_BORDER_WIDTH
        )

        # Draw text with a subtle shadow for better readability against the background
        draw.text(
            (text_x + Styles.TEXT_SHADOW_OFFSET[0], text_y + Styles.TEXT_SHADOW_OFFSET[1]),
            explanation_text,
            font=font,
            fill=Styles.TEXT_SHADOW_COLOR
        )
        draw.text((text_x, text_y), explanation_text, font=font, fill=Palette.TEXT_COLOR)

        # --- Professional Arrow from Text Box to Highlighted Object ---
        # Determine if the text box is positioned above or below the object
        is_text_above_object = (text_y + text_content_height / 2) < scaled_center_y

        # Define arrow start point based on the closest edge of the *text box border*
        if is_text_above_object:
            arrow_start_y = border_y2 # Arrow originates from the bottom edge of the text box border
        else:
            arrow_start_y = border_y1 # Arrow originates from the top edge of the text box border

        # Horizontal start point for the arrow, centered relative to the text box,
        # but clamped within the horizontal bounds of the text box border
        text_bg_center_x = (text_bg_x1 + text_bg_x2) // 2
        arrow_start_x = max(border_x1, min(border_x2, text_bg_center_x))

        line_start = (arrow_start_x, arrow_start_y)
        line_end = (scaled_center_x, scaled_center_y)

        # Draw arrow line shadow for depth
        shadow_line_start = (line_start[0] + Styles.ARROW_SHADOW_OFFSET[0], line_start[1] + Styles.ARROW_SHADOW_OFFSET[1])
        shadow_line_end = (line_end[0] + Styles.ARROW_SHADOW_OFFSET[0], line_end[1] + Styles.ARROW_SHADOW_OFFSET[1])
        draw.line([shadow_line_start, shadow_line_end], fill=Palette.SHADOW_COLOR, width=Styles.ARROW_WIDTH)

        # Draw the main arrow line
        draw.line([line_start, line_end], fill=Palette.ACCENT_ARROW, width=Styles.ARROW_WIDTH)

        # Calculate arrow head points for a sleek triangular shape
        angle = math.atan2(line_end[1] - line_start[1], line_end[0] - line_start[0])
        arrow_head_base_left = (line_end[0] - Styles.ARROW_HEAD_SIZE * math.cos(angle - math.pi / 6),
                                line_end[1] - Styles.ARROW_HEAD_SIZE * math.sin(angle - math.pi / 6))
        arrow_head_base_right = (line_end[0] - Styles.ARROW_HEAD_SIZE * math.cos(angle + math.pi / 6),
                                 line_end[1] - Styles.ARROW_HEAD_SIZE * math.sin(angle + math.pi / 6))
        arrow_head_points = [line_end, arrow_head_base_left, arrow_head_base_right]

        # Draw arrow head shadow
        arrow_head_points_shadow = [
            (p[0] + Styles.ARROW_SHADOW_OFFSET[0], p[1] + Styles.ARROW_SHADOW_OFFSET[1])
            for p in arrow_head_points
        ]
        draw.polygon(arrow_head_points_shadow, fill=Palette.SHADOW_COLOR)

        # Draw the main arrow head
        draw.polygon(arrow_head_points, fill=Palette.ACCENT_ARROW)

        # Ensure the output directory exists before saving
        output_dir = "temp"
        os.makedirs(output_dir, exist_ok=True)

        # Save the overlay image to the specified path
        # CRITICAL: This save command is preserved exactly as requested.
        overlay.save(os.path.join(output_dir, "overlay.png"))
        print(f"Overlay created and saved to {os.path.join(output_dir, 'overlay.png')}")

    except FileNotFoundError:
        print(f"Error: Screenshot file not found at '{screenshot_path}'. Please ensure the path is correct.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage:
# To run this, ensure you have a 'screenshot.png' file in the same directory
# as this script, or provide a full path to your screenshot.
# You might also want to ensure 'segoeui.ttf' or 'arial.ttf' is available on your system.
# On Windows, 'segoeui.ttf' is typically present by default.
if __name__ == "__main__":
    # Create a dummy screenshot for testing if it doesn't exist
    if not os.path.exists("screenshot.png"):
        print("Creating a dummy 'screenshot.png' for demonstration purposes.")
        dummy_img = Image.new('RGB', (1920, 1080), color = 'darkblue')
        dummy_draw = ImageDraw.Draw(dummy_img)
        # Draw some gold-like rectangles at the original bbox location
        dummy_draw.rectangle([600, 280, 800, 440], fill=(255, 215, 0)) # Gold color
        dummy_draw.rectangle([605, 285, 805, 445], fill=(255, 215, 0)) # Another bar
        dummy_draw.text((650, 350), "Gold Bars", fill=(0,0,0), font=ImageFont.load_default())
        dummy_img.save("screenshot.png")
        print("Dummy 'screenshot.png' created.")

    create_overlay("screenshot.png")
