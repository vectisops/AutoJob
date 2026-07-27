"""Lightweight company OSINT module.
Uses DuckDuckGo and Wikipedia REST APIs to fetch company details, websites,
and direct employer review links without external credentials.
"""
from typing import Dict, Any
import urllib.request
import urllib.parse
import json
import re


class CompanyIntel:
    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

    def lookup(self, company: str, location: str = "Australia") -> Dict[str, Any]:
        info: Dict[str, Any] = {
            "company": company,
            "summary": "",
            "website": "",
            "employee_rating": None,
            "rating_source": "",
            "notes": [],
            "lifestyle": "",
        }
        
        if not company or company.lower() in ("unknown", "n/a", ""):
            info["summary"] = "No company specified."
            return info

        # 1. Fetch summary & website via DuckDuckGo search HTML/API
        ddg_data = self._query_ddg(company)
        if ddg_data.get("website"):
            info["website"] = ddg_data["website"]
        if ddg_data.get("summary"):
            info["summary"] = ddg_data["summary"]

        # 2. Fallback to Wikipedia API if summary is sparse
        if len(info["summary"]) < 30:
            wiki_summary = self._query_wikipedia(company)
            if wiki_summary:
                info["summary"] = wiki_summary

        if not info["summary"]:
            info["summary"] = f"No public summary automatically found for '{company}'."

        # 3. Direct links for manual verification
        seek_query = urllib.parse.quote(f"{company} company reviews seek australia")
        glassdoor_query = urllib.parse.quote(f"{company} glassdoor reviews")
        linkedin_query = urllib.parse.quote(f"{company} linkedin company")

        info["notes"].extend([
            f"Seek Reviews Search: https://www.google.com/search?q={seek_query}",
            f"Glassdoor Search: https://www.google.com/search?q={glassdoor_query}",
            f"LinkedIn Page Search: https://www.google.com/search?q={linkedin_query}",
        ])

        # 4. Lifestyle / SEQ regional context
        loc_l = (location or "").lower()
        if any(x in loc_l for x in ("brisbane", "gold coast", "sunshine coast", "ipswich", "logan", "seq", "queensland")):
            info["lifestyle"] = (
                "SEQ lifestyle: strong outdoor/coastal culture and high work-life balance focus. "
                "Consider commute corridors (e.g., M1, Ipswich Motorway, Bruce Highway) and timezone (AEST, UTC+10)."
            )
        elif "remote" in loc_l:
            info["lifestyle"] = "Fully remote role – location flexibility; timezone alignment (AEST/AEDT) usually preferred for AU teams."

        return info

    def _query_ddg(self, company: str) -> Dict[str, str]:
        """Queries DuckDuckGo HTML to extract top snippet and company URL."""
        res = {"summary": "", "website": ""}
        try:
            query = urllib.parse.quote(f"{company} official website australia")
            url = f"https://html.duckduckgo.com/html/?q={query}"
            req = urllib.request.Request(url, headers=self.headers)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                html = response.read().decode("utf-8")

            # Extract first external link snippet
            snippets = re.findall(r'<a class="result__snippet[^">]*>(.*?)</a>', html, re.DOTALL)
            urls = re.findall(r'<a class="result__url"[^>]*>\s*(.*?)\s*</a>', html, re.DOTALL)

            if snippets:
                # Clean HTML tags from snippet
                clean_snippet = re.sub(r"<[^>]+>", "", snippets[0]).strip()
                res["summary"] = clean_snippet

            if urls:
                clean_url = re.sub(r"<[^>]+>", "", urls[0]).strip()
                if not clean_url.startswith("http"):
                    clean_url = "https://" + clean_url
                res["website"] = clean_url

        except Exception:
            pass  # Fail gracefully if offline or rate-limited

        return res

    def _query_wikipedia(self, company: str) -> str:
        """Fetches company overview from Wikipedia REST API."""
        try:
            formatted_name = urllib.parse.quote(company)
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_name}"
            req = urllib.request.Request(url, headers=self.headers)
            
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode("utf-8"))
                if data.get("type") == "standard" and "extract" in data:
                    return data["extract"]
        except Exception:
            pass
        return ""
