from pathlib import Path
from typing import List
import pandas as pd
from datetime import datetime

from src.models.job import Job
from src.utils.config import DATA_DIR


def export_to_excel(jobs: List[Job], filename: str | None = None) -> Path:
    if not filename:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"AutoJob_export_{ts}.xlsx"
    path = DATA_DIR / "exports" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for j in jobs:
        rows.append({
            "Score": round(j.score, 2),
            "Title": j.title,
            "Company": j.company,
            "Location": j.location,
            "Salary": j.salary_display,
            "Work Type": j.work_type,
            "Contract": j.contract_type,
            "Source": j.source,
            "Posted": j.posted_date or "",
            "URL": j.url or j.apply_url,
            "Match Reasons": "; ".join(j.match_reasons),
            "Description (excerpt)": (j.description or "")[:500],
        })
    df = pd.DataFrame(rows)
    try:
        df.to_excel(path, index=False, engine="openpyxl")
        return path
    except ModuleNotFoundError:
        # Fallback if openpyxl is not installed
        csv_path = path.with_suffix(".csv")
        df.to_csv(csv_path, index=False)
        return csv_path


def export_to_csv(jobs: List[Job], filename: str | None = None) -> Path:
    if not filename:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"AutoJob_export_{ts}.csv"
    path = DATA_DIR / "exports" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([j.to_dict() for j in jobs]).to_csv(path, index=False)
    return path
