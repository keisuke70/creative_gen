import os
import openai
from dotenv import load_dotenv

load_dotenv()


def generate_copy(summary: str, n: int = 3) -> list:
    """Generate copy variants from summary."""
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        openai.api_key = api_key
        try:
            response = openai.chat.completions.create(
                model='gpt-4o-mini',
                messages=[{"role": "system", "content": "Write short ad copy"},
                          {"role": "user", "content": summary}],
                n=n,
                max_tokens=20,
                temperature=0.9
            )
            return [c.message.content.strip() for c in response.choices]
        except Exception:
            pass
    # fallback simple copies
    return [f"Buy now: {summary[:40]}" for _ in range(n)]
