from pathlib import Path
from typing import Iterable
from PIL import Image, ImageDraw, ImageFont
import yaml

from .background_mixer import create_background


# load sizes
sizes_file = Path(__file__).resolve().parent.parent / 'config' / 'creative_sizes.yml'
with open(sizes_file, 'r') as f:
    CREATIVE_SIZES = yaml.safe_load(f)['sizes']


def compose_banners(product_image: Image.Image, copy_lines: Iterable[str], strategy='layer', out_dir=Path('.')) -> list:
    """Compose banners and save PNG files. Returns list of file paths."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    paths = []
    for idx, copy in enumerate(copy_lines):
        for w, h in CREATIVE_SIZES:
            bg = create_background((w, h), strategy)
            img = product_image.copy()
            img.thumbnail((int(w*0.8), int(h*0.6)))
            paste_x = (w - img.width) // 2
            paste_y = (h - img.height) // 2
            bg.paste(img, (paste_x, paste_y), img)

            draw = ImageDraw.Draw(bg)
            draw.text((5, h - 15), copy[:40], fill='black', font=font)
            filename = out_dir / f'banner_{idx}_{w}x{h}.png'
            bg.save(filename)
            paths.append(filename)
    return paths
