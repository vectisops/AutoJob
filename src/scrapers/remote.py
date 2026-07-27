"""Lightweight free remote job sources (no key required)."""
from typing import List, Dict, Any
import requests
from src.models.job import Job
from src.scrapers.base import BaseScraper


class RemotiveScraper(BaseScraper):
    name = "Remotive"
    URL = "https://remotive.com/api/remote-jobs"

    def search(self, query: Dict[str, Any]) -> List[Job]:
        keywords = (query.get("keywords") or "").lower()
        jobs = []
        try:
            resp = requests.get(self.URL, timeout=20)
            resp.raise_for_status()
            for r in resp.json().get("jobs", [])[:80]:
                title = r.get("title", "")
                if keywords and keywords not in title.lower() and keywords not in (r.get("description") or "").lower():
                    continue
                jobs.append(Job(
                    id=f"remotive-{r.get('id')}",
                    title=title,
                    company=r.get("company_name", "Unknown"),
                    location="Remote",
                    description=(r.get("description") or "")[:2000],
                    url=r.get("url", ""),
                    apply_url=r.get("url", ""),
                    source="Remotive",
                    work_type="remote",
                    category=r.get("category", ""),
                    posted_date=r.get("publication_date"),
                ))
        except Exception as e:
            print(f"[Remotive] {e}")
        return jobs


class JobicyScraper(BaseScraper):
    name = "Jobicy"
    URL = "https://jobicy.com/api/v2/remote-jobs"

    def search(self, query: Dict[str, Any]) -> List[Job]:
        keywords = (query.get("keywords") or "").lower()
        jobs = []
        try:
            resp = requests.get(self.URL, params={"count": 50}, timeout=20)
            resp.raise_for_status()
            for r in resp.json().get("jobs", []):
                title = r.get("jobTitle", "")
                if keywords and keywords not in title.lower():
                    continue
                jobs.append(Job(
                    id=f"jobicy-{r.get('id')}",
                    title=title,
                    company=r.get("companyName", "Unknown"),
                    location=r.get("jobGeo", "Remote") or "Remote",
                    description=(r.get("jobDescription") or "")[:2000],
                    url=r.get("url", ""),
                    apply_url=r.get("url", ""),
                    source="Jobicy",
                    work_type="remote",
                    salary_raw=r.get("annualSalaryMin") and f"{r.get('annualSalaryMin')}-{r.get('annualSalaryMax')}" or "",
                    posted_date=r.get("pubDate"),
                ))
        except Exception as e:
            print(f"[Jobicy] {e}")
        return jobs
