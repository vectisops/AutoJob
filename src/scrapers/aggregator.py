"""Lightweight job aggregator for a single user.

Runs a small number of sources in parallel (max a few workers) and
returns a modest set of results. Built for personal job hunting,
not large-scale scraping.
"""
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

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

        # Free remote sources – only used when the user asks for remote roles
        self.remote_scrapers = [RemotiveScraper(), JobicyScraper()]

    def search(self, query: Dict[str, Any], include_remote: bool = False) -> List[Job]:
        all_jobs: List[Job] = []
        scrapers = list(self.scrapers)
        if include_remote or "remote" in (query.get("location") or "").lower():
            scrapers.extend(self.remote_scrapers)

        def run(s):
            try:
                return s.search(query)
            except Exception as e:
                print(f"[{s.name}] failed: {e}")
                return []

        # Small worker pool – this is personal use, not high-volume crawling
        with ThreadPoolExecutor(max_workers=4) as ex:
            futures = {ex.submit(run, s): s for s in scrapers}
            for fut in as_completed(futures):
                jobs = fut.result()
                all_jobs.extend(jobs)

        # Simple de-duplication by title + company
        seen = set()
        unique = []
        for j in all_jobs:
            key = (j.title.lower().strip(), j.company.lower().strip())
            if key not in seen:
                seen.add(key)
                unique.append(j)
        return unique
