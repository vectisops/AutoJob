"""Job aggregator for a single personal user.

Pulls from a few sources (typically a few hundred results total) so
niche roles are less likely to be missed, then the rest of the app
ranks and returns only the best matches (default max 30).
Built for individual job hunting, not continuous bulk harvesting.
"""
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import inspect
import asyncio

from src.models.job import Job
from src.scrapers.adzuna import AdzunaScraper
from src.scrapers.seek import SeekScraper
from src.scrapers.remote import RemotiveScraper, JobicyScraper
from src.utils.config import Config


class JobAggregator:
    def __init__(self, config: Config):
        self.config = config
        self.scrapers = []

        app_id = config.get("adzuna_app_id", "")
        app_key = config.get("adzuna_app_key", "")
        if app_id and app_key:
            self.scrapers.append(AdzunaScraper(app_id, app_key, country=config.get("default_country", "au")))

        profile = config.get("seek_profile_dir")
        self.scrapers.append(SeekScraper(profile, headless=config.get("browser_headless", True)))

        self.remote_scrapers = [RemotiveScraper(), JobicyScraper()]

    def search(self, query: Dict[str, Any], include_remote: bool = False) -> List[Job]:
        all_jobs: List[Job] = []
        scrapers = list(self.scrapers)
        if include_remote or "remote" in (query.get("location") or "").lower():
            scrapers.extend(self.remote_scrapers)

        def run(s):
            name = getattr(s, "name", type(s).__name__)
            try:
                # Support both sync and async search() implementations
                if inspect.iscoroutinefunction(s.search):
                    return asyncio.run(s.search(query))
                result = s.search(query)
                # Guard: if a sync wrapper returned a coroutine by mistake
                if inspect.iscoroutine(result):
                    return asyncio.run(result)
                return result or []
            except Exception as e:
                print(f"[{name}] failed: {e}")
                return []

        with ThreadPoolExecutor(max_workers=4) as ex:
            futures = {ex.submit(run, s): s for s in scrapers}
            for fut in as_completed(futures):
                jobs = fut.result()
                if jobs:
                    all_jobs.extend(jobs)

        # De-dupe within this run (prefer URL when present)
        seen = set()
        unique = []
        for j in all_jobs:
            url = (j.url or j.apply_url or "").strip().lower()
            if url and len(url) > 10:
                key = ("url", url)
            else:
                key = (
                    "tc",
                    (j.title or "").lower().strip(),
                    (j.company or "").lower().strip(),
                    (j.location or "").lower().strip(),
                )
            if key not in seen:
                seen.add(key)
                unique.append(j)
        return unique
