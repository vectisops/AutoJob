"""Adzuna API client for personal job searching in Australia.

Designed for individual use only. Keeps result pages low by default
and is not intended for bulk or continuous harvesting of listings.
"""
from typing import List, Dict, Any, Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.models.job import Job
from src.scrapers.base import BaseScraper


class AdzunaScraper(BaseScraper):
    name = "Adzuna"
    BASE = "https://api.adzuna.com/v1/api/jobs"

    def __init__(self, app_id: str, app_key: str, country: str = "au"):
        self.app_id = app_id
        self.app_key = app_key
        self.country = country.lower()

    def _params(self, page: int, query: Dict[str, Any]) -> Dict[str, Any]:
        p = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": query.get("results_per_page", 50),
            "content-type": "application/json",
        }
        if query.get("keywords"):
            p["what"] = query["keywords"]
        if query.get("location"):
            p["where"] = query["location"]
        if query.get("salary_min"):
            p["salary_min"] = int(query["salary_min"])
        if query.get("salary_max"):
            p["salary_max"] = int(query["salary_max"])
        if query.get("full_time"):
            p["full_time"] = 1
        if query.get("contract"):
            p["contract"] = 1
        if query.get("sort_by"):
            p["sort_by"] = query["sort_by"]
        return p

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _fetch_page(self, page: int, query: Dict[str, Any]) -> Dict:
        url = f"{self.BASE}/{self.country}/search/{page}"
        resp = requests.get(url, params=self._params(page, query), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def search(self, query: Dict[str, Any]) -> List[Job]:
        if not self.app_id or not self.app_key:
            return []
        jobs: List[Job] = []
        # Deliberately modest page limit for personal use
        max_pages = min(query.get("max_pages", 3), 5)
        for page in range(1, max_pages + 1):
            try:
                data = self._fetch_page(page, query)
            except Exception as e:
                print(f"[Adzuna] page {page} failed: {e}")
                break
            results = data.get("results", [])
            if not results:
                break
            for r in results:
                job = self._parse(r)
                if job:
                    jobs.append(job)
            if len(results) < query.get("results_per_page", 50):
                break
        return jobs

    def _parse(self, r: Dict) -> Optional[Job]:
        try:
            loc = r.get("location", {})
            area = ", ".join(loc.get("area", [])) if isinstance(loc.get("area"), list) else str(loc.get("display_name", ""))
            salary_min = r.get("salary_min")
            salary_max = r.get("salary_max")
            return Job(
                id=f"adzuna-{r.get('id')}",
                title=r.get("title", "").strip(),
                company=r.get("company", {}).get("display_name", "Unknown"),
                location=area or r.get("location", {}).get("display_name", ""),
                description=r.get("description", "") or "",
                salary_min=float(salary_min) if salary_min else None,
                salary_max=float(salary_max) if salary_max else None,
                salary_raw=r.get("salary_is_predicted", "") and "Predicted" or "",
                url=r.get("redirect_url", ""),
                apply_url=r.get("redirect_url", ""),
                source="Adzuna",
                posted_date=r.get("created"),
                contract_type=r.get("contract_type", ""),
                work_type=r.get("contract_time", ""),
                category=r.get("category", {}).get("label", ""),
                raw=r,
            )
        except Exception:
            return None
