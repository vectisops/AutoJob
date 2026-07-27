from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any


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
    work_type: str = ""
    experience_level: str = ""
    category: str = ""
    company_url: str = ""
    score: float = 0.0
    match_reasons: List[str] = field(default_factory=list)
    osint: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def salary_display(self) -> str:
        # Prefer numeric range; annotate predicted salaries instead of hiding the numbers
        predicted = (self.salary_raw or "").strip().lower() == "predicted"

        if self.salary_min is not None and self.salary_max is not None:
            s = f"${self.salary_min:,.0f} – ${self.salary_max:,.0f}"
            return f"{s} (Predicted)" if predicted else s
        if self.salary_min is not None:
            s = f"From ${self.salary_min:,.0f}"
            return f"{s} (Predicted)" if predicted else s
        if self.salary_max is not None:
            s = f"Up to ${self.salary_max:,.0f}"
            return f"{s} (Predicted)" if predicted else s
        if self.salary_raw:
            return self.salary_raw
        return "Not specified"
