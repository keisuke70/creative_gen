import os
import json
import zipfile
import requests


LOGICAD_ENDPOINT = 'https://logicad.example.com/v1/upload'


def upload_to_logicad(zip_path: str, meta: dict, dry_run: bool = False) -> None:
    """Upload zip and metadata to Logicad."""
    if dry_run:
        print(f"[dry-run] Would upload {zip_path} with meta {meta}")
        return
    token = os.getenv('LOGICAD_TOKEN')
    if not token:
        raise RuntimeError('LOGICAD_TOKEN not set')
    with open(zip_path, 'rb') as f:
        files = {'file': (os.path.basename(zip_path), f, 'application/zip')}
        data = {'meta': json.dumps(meta)}
        headers = {'Authorization': f'Bearer {token}'}
        requests.post(LOGICAD_ENDPOINT, files=files, data=data, headers=headers)
