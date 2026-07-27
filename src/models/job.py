from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class Job:
    id: str
    title: str
    company: str
    location: str
    description: str = ""
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_raw: str = ""
    url: str = ""
    apply_url: str = ""
    source: str = ""
    posted_date: Optional[str] = None
    contract_type: str = ""
    work_type: str = ""  # full-time, part-time, contract, casual, hybrid, remote
    experience_level: str = ""
    category: str = ""
    company_url: str = ""
    score: float = 0.0
    match_reasons: List[str] = field(default_factory=list)
    osint: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    @property
    def salary_display(self) -> str:
        if self.salary_raw:
            return self.salary_raw
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,.0f} – ${self.salary_max:,.0f}"
        if self.salary_min:
            return f"From ${self.salary_min:,.0f}"
        if self.salary_max:
            return f"Up to ${self.salary_max:,.0f}"
        return "Not specified"
