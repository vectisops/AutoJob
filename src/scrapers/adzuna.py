"""Adzuna API client for personal job searching in Australia.

Collects a few hundred results when needed so niche roles can surface,
then the app ranks and returns only the best matches (max 30) to the user.
Still intended for personal use only — not continuous bulk harvesting.
"""
from typing import List, Dict, Any, Optional
import re
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

    @staticmethod
    def _clean_html(text: str) -> str:
        if not text:
            return ""
        # Strip highlight tags Adzuna inserts around matched keywords
        return re.sub(r"<[^>]+>", "", text).strip()

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
        # Only send when explicitly truthy / 1 — avoid conflicting flags
        if query.get("full_time") is True or query.get("full_time") == 1:
            p["full_time"] = 1
        if query.get("contract") is True or query.get("contract") == 1:
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
        max_pages = min(int(query.get("max_pages", 8)), 12)
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
            area = (
                ", ".join(loc.get("area", []))
                if isinstance(loc.get("area"), list)
                else str(loc.get("display_name", ""))
            )
            salary_min = r.get("salary_min")
            salary_max = r.get("salary_max")
            title = self._clean_html(r.get("title", ""))
            description = self._clean_html(r.get("description", "") or "")
            return Job(
                id=f"adzuna-{r.get('id')}",
                title=title,
                company=r.get("company", {}).get("display_name", "Unknown"),
                location=area or r.get("location", {}).get("display_name", ""),
                description=description,
                salary_min=float(salary_min) if salary_min is not None else None,
                salary_max=float(salary_max) if salary_max is not None else None,
                salary_raw="Predicted" if r.get("salary_is_predicted") else "",
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
