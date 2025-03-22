from PIL import Image, ImageDraw
import os

def create_icon():
    # Create a new image with a transparent background
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a blue circle
    margin = 20
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill='#4a9eff'
    )
    
    # Draw "SH" text
    from PIL import ImageFont
    try:
        font = ImageFont.truetype("arial.ttf", 100)
    except:
        font = ImageFont.load_default()
    
    # Add text
    text = "SH"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    draw.text((x, y), text, fill='white', font=font)
    
    # Save as ICO
    if not os.path.exists('assets/images'):
        os.makedirs('assets/images')
    image.save('assets/images/icon.ico', format='ICO')

if __name__ == "__main__":
    create_icon() 