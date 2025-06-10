import io
import requests
from bs4 import BeautifulSoup
from PIL import Image


def fetch_product_image(lp_url: str) -> Image.Image:
    """Fetch the first image from the landing page."""
    if lp_url.startswith('file://'):
        with open(lp_url[len('file://'):], 'r', encoding='utf-8') as f:
            html = f.read()
    else:
        resp = requests.get(lp_url, timeout=10)
        resp.raise_for_status()
        html = resp.text
    soup = BeautifulSoup(html, 'html.parser')
    img_tag = soup.find('img')
    if not img_tag or not img_tag.get('src'):
        raise ValueError('No image found')
    src = img_tag['src']
    if src.startswith('//'):
        src = 'https:' + src
    if src.startswith('/'):
        from urllib.parse import urljoin
        src = urljoin(lp_url, src)
    img_resp = requests.get(src, timeout=10)
    img_resp.raise_for_status()
    return Image.open(io.BytesIO(img_resp.content)).convert('RGBA')
