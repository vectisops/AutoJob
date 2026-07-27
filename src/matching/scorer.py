from typing import List, Set, Dict, Any
from src.models.job import Job


class JobScorer:
    def __init__(self, resume_keywords: Set[str] | None = None, exclude: List[str] | None = None):
        self.resume_keywords = resume_keywords or set()
        self.exclude = [e.lower().strip() for e in (exclude or []) if e.strip()]

    def score(self, jobs: List[Job], query: Dict[str, Any]) -> List[Job]:
        include_kw = [k.lower().strip() for k in (query.get("include_keywords") or []) if k.strip()]
        for job in jobs:
            reasons = []
            score = 0.0
            text = f"{job.title} {job.company} {job.description} {job.location}".lower()

            if any(ex in text for ex in self.exclude):
                job.score = -1
                job.match_reasons = ["Excluded by keyword"]
                continue

            title_l = job.title.lower()
            for kw in include_kw:
                if kw in title_l:
                    score += 25
                    reasons.append(f"Title contains '{kw}'")
                elif kw in text:
                    score += 10
                    reasons.append(f"Description contains '{kw}'")

            if self.resume_keywords:
                job_tokens = set(text.split())
                overlap = self.resume_keywords & job_tokens
                if overlap:
                    contrib = min(40, len(overlap) * 1.5)
                    score += contrib
                    reasons.append(f"Resume overlap: {', '.join(list(overlap)[:5])}")

            loc_pref = [l.lower() for l in (query.get("preferred_locations") or [])]
            job_loc = job.location.lower()
            for loc in loc_pref:
                if loc in job_loc or (loc == "remote" and "remote" in job_loc):
                    score += 15
                    reasons.append(f"Location match: {loc}")
                    break

            smin = query.get("salary_min") or 0
            if smin and job.salary_min and job.salary_min >= smin:
                score += 10
                reasons.append("Meets salary min")

            if job.source in ("Seek", "Adzuna"):
                score += 5

            job.score = round(score, 1)
            job.match_reasons = reasons

        valid = [j for j in jobs if j.score >= 0]
        valid.sort(key=lambda j: j.score, reverse=True)
        return valid
