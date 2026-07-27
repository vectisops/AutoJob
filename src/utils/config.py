import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"
SETTINGS_PATH = CONFIG_DIR / "settings.json"
EXAMPLE_PATH = CONFIG_DIR / "settings.example.json"

DEFAULT_SETTINGS = {
    # Personal use – broader collection so niche roles can surface,
    # then only the best matches are shown (max 30).
    "adzuna_app_id": "",
    "adzuna_app_key": "",
    "default_country": "au",
    "results_per_page": 50,
    "max_pages": 8,
    "top_results": 30,
    "theme": "dark",
    "browser_headless": False,
    "seek_profile_dir": str(DATA_DIR / "browser_profiles" / "seek"),
    "resume_path": "",
    "last_locations": ["Brisbane", "SEQ"],
    "last_titles": [],
    "exclude_keywords": ["unpaid", "volunteer", "internship (unpaid)"],
    "salary_min": 0,
    "salary_max": 0,
    "history_file": str(DATA_DIR / "history" / "job_history.json"),
}


class Config:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "browser_profiles").mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "exports").mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "resumes").mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "history").mkdir(parents=True, exist_ok=True)
        self._data: Dict[str, Any] = {}
        self.load()

    def load(self):
        if SETTINGS_PATH.exists():
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = DEFAULT_SETTINGS.copy()
        else:
            self._data = DEFAULT_SETTINGS.copy()
            self.save()
            with open(EXAMPLE_PATH, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_SETTINGS, f, indent=2)

    def save(self):
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        self._data[key] = value
        self.save()

    def update(self, mapping: Dict[str, Any]):
        self._data.update(mapping)
        self.save()

    @property
    def data(self) -> Dict[str, Any]:
        return self._data
