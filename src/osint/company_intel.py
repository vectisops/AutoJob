"""Lightweight company OSINT. Best-effort public data only."""
from typing import Dict, Any


class CompanyIntel:
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
            return info

        info["notes"].append(
            "Full Glassdoor/Seek company ratings often require manual check or authenticated browser."
        )
        info["summary"] = f"Search for '{company}' reviews on Seek employer pages or Glassdoor for employee ratings."

        loc_l = (location or "").lower()
        if any(x in loc_l for x in ("brisbane", "gold coast", "sunshine coast", "ipswich", "logan", "seq", "queensland")):
            info["lifestyle"] = (
                "SEQ lifestyle: generally good work-life balance, outdoor culture, "
                "higher cost of living in inner Brisbane / Gold Coast, more affordable in outer suburbs. "
                "Traffic and flood risk are known considerations in some areas."
            )
        elif "remote" in loc_l:
            info["lifestyle"] = "Fully remote role – location flexibility; timezone (AEST/AEDT) still relevant for AU teams."

        return info
