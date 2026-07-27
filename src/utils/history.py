"""Simple local job history for personal use.

Stores previously seen jobs so subsequent scrapes can drop duplicates.
Everything stays on the user's machine only.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Set, Dict, Any
from datetime import datetime
from urllib.parse import urlparse

from src.models.job import Job
from src.utils.config import DATA_DIR

HISTORY_DIR = DATA_DIR / "history"
HISTORY_FILE = HISTORY_DIR / "job_history.json"
MAX_HISTORY = 2000


def _job_key(job: Job) -> str:
    """Stable key for de-duplication.

    Prefer a URL with query params stripped (tracking params change every scrape).
    Fall back to title + company + location.
    """
    url = (job.url or job.apply_url or "").strip().lower()
    if url and len(url) > 10:
        parsed = urlparse(url)
        clean = f"{parsed.netloc}{parsed.path}".rstrip("/")
        if len(clean) > 10:
            return f"url:{clean}"
    title = (job.title or "").strip().lower()
    company = (job.company or "").strip().lower()
    location = (job.location or "").strip().lower()
    return f"tcl:{title}|{company}|{location}"


def load_history(path: Path | None = None) -> Dict[str, Any]:
    path = path or HISTORY_FILE
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        return {"seen_keys": [], "last_updated": None, "jobs": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "seen_keys" not in data:
            data["seen_keys"] = []
        return data
    except Exception:
        return {"seen_keys": [], "last_updated": None, "jobs": []}


def save_history(jobs: List[Job], path: Path | None = None) -> None:
    path = path or HISTORY_FILE
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    data = load_history(path)
    # Cumulative set — never rebuild only from the capped jobs list
    seen: Set[str] = set(data.get("seen_keys") or [])

    for j in jobs:
        key = _job_key(j)
        if key not in seen:
            seen.add(key)
            data.setdefault("jobs", []).append({
                "key": key,
                "title": j.title,
                "company": j.company,
                "url": j.url or j.apply_url,
                "source": j.source,
                "seen_at": datetime.now().isoformat(timespec="seconds"),
            })

    # Cap detailed log size only; keep full seen_keys so old jobs stay filtered
    if len(data.get("jobs", [])) > MAX_HISTORY:
        data["jobs"] = data["jobs"][-MAX_HISTORY:]

    data["seen_keys"] = list(seen)
    data["last_updated"] = datetime.now().isoformat(timespec="seconds")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def filter_new_jobs(jobs: List[Job], path: Path | None = None) -> List[Job]:
    data = load_history(path)
    seen: Set[str] = set(data.get("seen_keys") or [])
    return [j for j in jobs if _job_key(j) not in seen]
