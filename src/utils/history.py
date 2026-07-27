"""Simple local job history for personal use.

Stores previously seen jobs so subsequent scrapes can drop duplicates.
Everything stays on the user's machine only.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Set, Dict, Any
from datetime import datetime

from src.models.job import Job
from src.utils.config import DATA_DIR


HISTORY_DIR = DATA_DIR / "history"
HISTORY_FILE = HISTORY_DIR / "job_history.json"
MAX_HISTORY = 2000  # keep a reasonable personal history size


def _job_key(job: Job) -> str:
    """Stable key for de-duplication (prefer URL, fall back to title+company)."""
    url = (job.url or job.apply_url or "").strip().lower()
    if url and len(url) > 10:
        return f"url:{url}"
    title = (job.title or "").strip().lower()
    company = (job.company or "").strip().lower()
    return f"tc:{title}|{company}"


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
    """Merge new jobs into history and write back (personal local store only)."""
    path = path or HISTORY_FILE
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    data = load_history(path)
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

    if len(data["jobs"]) > MAX_HISTORY:
        data["jobs"] = data["jobs"][-MAX_HISTORY:]
        seen = {item["key"] for item in data["jobs"]}

    data["seen_keys"] = list(seen)
    data["last_updated"] = datetime.now().isoformat(timespec="seconds")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def filter_new_jobs(jobs: List[Job], path: Path | None = None) -> List[Job]:
    """Return only jobs not already present in local history."""
    data = load_history(path)
    seen: Set[str] = set(data.get("seen_keys") or [])
    new_jobs = []
    for j in jobs:
        key = _job_key(j)
        if key not in seen:
            new_jobs.append(j)
    return new_jobs
