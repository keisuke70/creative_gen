import os
import requests
from bs4 import BeautifulSoup

import openai
from dotenv import load_dotenv

load_dotenv()


def parse_lp(url: str) -> str:
    """Fetches a landing page and returns a short summary."""
    if url.startswith('file://'):
        with open(url[len('file://'):], 'r', encoding='utf-8') as f:
            html = f.read()
    else:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        html = resp.text
    soup = BeautifulSoup(html, 'html.parser')
    text = ' '.join(p.get_text(separator=' ', strip=True) for p in soup.find_all('p'))
    if not text:
        text = soup.get_text(separator=' ', strip=True)
    text = text.strip()
    if not text:
        return ''

    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        openai.api_key = api_key
        try:
            response = openai.chat.completions.create(
                model='gpt-4o-mini',
                messages=[{"role": "system", "content": "Summarize the landing page content"},
                          {"role": "user", "content": text}],
                max_tokens=60
            )
            return response.choices[0].message.content.strip()
        except Exception:
            pass
    # fallback naive summary
    return text[:200]
