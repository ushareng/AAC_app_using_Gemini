from PIL import Image, ImageFont, ImageDraw, ImageColor
import io
import base64
from typing import Tuple

def text_to_image(
    text: str,
    font_filepath: str = "font.ttf",
    font_size: int = 24,
    color: Tuple[int, int, int, int] = (0, 128, 0, 255),  # Default color (red)
    
) -> None:
    font = ImageFont.truetype(font_filepath, size=font_size)

    img = Image.new("RGBA", font.getmask(text).size)

    draw = ImageDraw.Draw(img)
    draw_point = (0, 0)

    draw.multiline_text(draw_point, text, font=font, fill=color)

    text_window = img.getbbox()
    img = img.crop(text_window)

    # Get the dimensions of the cropped image
    width, height = img.size

    # Determine the size of the new square image
    square_size = max(width, height)

    # Create a new square image with a transparent background
    square_img = Image.new("RGBA", (square_size, square_size), (0, 0, 0, 0))

    # Paste the original image onto the center of the square image
    paste_position = ((square_size - width) // 2, (square_size - height) // 2)
    square_img.paste(img, paste_position)
    buffered = io.BytesIO()
    
    # Save the image to the buffer in PNG format (you can change the format if needed)
    square_img.save(buffered, format="PNG")
    
    # Get the byte data from the buffer
    img_bytes = buffered.getvalue()
    
    # Encode the byte data to base64
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    #img.save(output_filepath)
    #print(img_base64)

    return img_base64


# colors 
# rgba(2, 22, 115, 0.92) - dark blue 
# rgba(89, 0, 0, 0.92) maroon 
# rgba(255, 0, 0, 0.92) red 
# rgba(32, 109, 32, 1) dark green 
# rgba(19, 111, 129, 1) dark cyan 
# rgba(66, 11, 103, 1) dark purple 