from datetime import date
from pathlib import Path

import requests

URL = "https://www.amfiindia.com/spages/NAVAll.txt"
RAW_DIR = Path("data/raw")


def download_nav():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    response = requests.get(URL, timeout=60)
    response.raise_for_status()

    out_file = RAW_DIR / f"NAVAll_{date.today().isoformat()}.txt"
    out_file.write_bytes(response.content)
    print(f"Saved {len(response.content):,} bytes to {out_file}")


if __name__ == "__main__":
    download_nav()