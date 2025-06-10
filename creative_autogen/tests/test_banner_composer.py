from pathlib import Path
from PIL import Image

from creative_autogen.src.banner_composer import compose_banners


def test_banner_size():
    img = Image.new('RGBA', (400, 300), (255, 0, 0, 255))
    paths = compose_banners(img, ["Test copy"], out_dir=Path('test_output'))
    assert paths, 'No banners produced'
    sample = Path(paths[0])
    with Image.open(sample) as im:
        assert im.size in [(300, 250), (728, 90), (160, 600), (300, 600), (970, 250), (320, 50), (468, 60), (120, 600)]
