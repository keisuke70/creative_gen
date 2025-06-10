# creative_autogen

This proof-of-concept CLI generates ad creatives from a landing page URL.

## Setup

```bash
pip install -r creative_autogen/requirements.txt
```

## Usage

```bash
python -m creative_autogen.src.main <LP_URL> --strategy layer --dry-run
```

Use `--dry-run` to skip uploading to Logicad.

