import argparse
import json
import zipfile
from pathlib import Path

from dotenv import load_dotenv

from .lp_parser import parse_lp
from .copy_generator import generate_copy
from .image_fetcher import fetch_product_image
from .banner_composer import compose_banners
from .logicad_uploader import upload_to_logicad


def pipeline(lp_url: str, strategy: str, dry_run: bool):
    summary = parse_lp(lp_url)
    if not summary:
        raise RuntimeError('Summary is empty')
    copies = generate_copy(summary, n=3)
    product_image = fetch_product_image(lp_url)
    out_dir = Path('output')
    banners = compose_banners(product_image, copies, strategy=strategy, out_dir=out_dir)

    zip_path = out_dir / 'banners.zip'
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for path in banners:
            zf.write(path, path.name)
    meta = {'summary': summary, 'copies': copies}
    with open(out_dir / 'meta.json', 'w') as f:
        json.dump(meta, f)
    upload_to_logicad(str(zip_path), meta, dry_run=dry_run)


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description='Generate creatives from LP URL')
    parser.add_argument('url')
    parser.add_argument('--strategy', default='layer')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    pipeline(args.url, args.strategy, args.dry_run)


if __name__ == '__main__':
    main()
