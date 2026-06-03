# scripts/create_api_client.py

import argparse
import hashlib
import secrets
import sys
import traceback
from pathlib import Path

# Add the parent directory to Python path so we can import from app
script_dir = Path(__file__).parent
app_dir = script_dir.parent
sys.path.insert(0, str(app_dir))

from app.db.session import get_db
from app.domains.api_clients.models import APIClient

def create_api_key(name: str) -> str:
    raw_key = secrets.token_urlsafe(32)
    hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()

    db = next(get_db())
    client = APIClient(name=name, api_key=hashed_key)
    db.add(client)
    db.commit()

    print(f"✅ API key created for '{name}'")
    print(f"🔑 Here is the API key (save it securely!):\n\n{raw_key}\n")
    return raw_key

def main():
    parser = argparse.ArgumentParser(description="Create an API client")
    parser.add_argument('--name', required=True, help="Name of the API client")
    args = parser.parse_args()

    try:
        create_api_key(args.name)
    except Exception:
        print("❌ Failed to create API key:")
        traceback.print_exc()

main()  # <- Ensures the function runs even when using `python -m`
