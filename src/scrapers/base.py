from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.models.job import Job


class BaseScraper(ABC):
    """Base class for personal job-search helpers."""
    name: str = "base"

    @abstractmethod
    def search(self, query: Dict[str, Any]) -> List[Job]:
        """Return a modest list of jobs matching the user's query."""
        pass
