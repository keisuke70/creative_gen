from PIL import Image, ImageDraw


def create_background(size, strategy='layer') -> Image.Image:
    """Create a plain background image."""
    if strategy == 'layer':
        bg = Image.new('RGBA', size, (255, 255, 255, 255))
    else:
        bg = Image.new('RGBA', size, (240, 240, 240, 255))
    return bg
