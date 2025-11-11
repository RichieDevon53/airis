from app.utils.screenshot import gettemp
import base64
from io import BytesIO
from PIL import Image
import os

def prepare_images(quality: int = 50, delete_after_convert: bool = False, is_direct: bool = False):
    """
    Prepare and compress images from temp.png file
    
    Args:
        quality (int): JPEG compression quality (1-100)
        delete_after_convert (bool): Whether to delete source file after conversion
        
    Returns:
        list: List containing processed image data
    """
    image_contents = None
    
    try:
        with Image.open(gettemp()) as image:
            # Convert and compress image
            compressed_io = BytesIO()
            image.convert("RGB").save(
                compressed_io, 
                format="JPEG",
                optimize=True,
                quality=quality
            )
            compressed_io.seek(0)
            
            # Encode to base64
            compressed_base64 = base64.b64encode(compressed_io.read()).decode("utf-8")
            
            image_contents = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{compressed_base64}"
                }
            }
            
    except Exception as e:
        print(f"Failed to process image: {e}")
        
    if not image_contents:
        print("Warning: No images were successfully processed")
        
    if delete_after_convert:
        try:
            os.remove(gettemp)
        except Exception as e:
            print(f"Failed to delete temporary file: {e}")
            
    if is_direct:
        return f"data:image/jpeg;base64,{compressed_base64}"
    return image_contents


