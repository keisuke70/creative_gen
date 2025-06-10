# creative_autogen

This proof-of-concept CLI generates ad creatives from a landing page URL.

## Setup

```bash
pip install -r creative_autogen/requirements.txt
```

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Set values for:

- `OPENAI_API_KEY`
- `SHOPIFY_TOKEN`
- `AMAZON_PAAPI_KEY`
- `GOOGLE_CLOUD_CREDENTIALS`
- `LOGICAD_TOKEN`
- `PINECONE_API_KEY`

## Usage

```bash
python -m creative_autogen.src.main <LP_URL> --strategy layer --dry-run
```

Use `--dry-run` to skip uploading to Logicad.

