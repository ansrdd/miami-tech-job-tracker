"""Fetch raw job postings from public ATS job board APIs."""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

RAW_DIR = Path("data/raw")
GREENHOUSE_URL = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
TIMEOUT_SECONDS = 15


def fetch_greenhouse(slug: str) -> list[dict]:
    """Return all published jobs from one company's Greenhouse board."""
    response = requests.get(
        GREENHOUSE_URL.format(slug=slug),
        params={"content": "true"},  # include full job descriptions
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()  # turn 404/500 errors into exceptions
    return response.json()["jobs"]


def save_raw(source: str, slug: str, jobs: list[dict]) -> Path:
    """Save the untouched API response so we can re-process it later."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RAW_DIR / f"{source}_{slug}_{stamp}.json"
    path.write_text(json.dumps(jobs, indent=2))
    return path


def main() -> None:
    for slug in ["stripe", "gitlab", "figma"]:
        try:
            jobs = fetch_greenhouse(slug)
        except requests.RequestException as err:
            print(f"[greenhouse:{slug}] failed: {err}")
            continue
        path = save_raw("greenhouse", slug, jobs)
        print(f"[greenhouse:{slug}] saved {len(jobs)} jobs -> {path}")
        time.sleep(1)  # be polite to their servers


if __name__ == "__main__":
    main()