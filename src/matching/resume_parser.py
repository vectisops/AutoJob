from pathlib import Path
from typing import Optional, Set


class ResumeParser:
    def __init__(self):
        self.text: str = ""
        self.path: Optional[Path] = None

    def load(self, path: str | Path) -> str:
        path = Path(path)
        self.path = path
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            self.text = self._pdf(path)
        elif suffix == ".docx":
            self.text = self._docx(path)
        elif suffix == ".doc":
            # python-docx cannot parse legacy binary .doc
            print(
                "[ResumeParser] Legacy .doc is not supported. Please convert to .docx or PDF."
            )
            self.text = ""
        else:
            self.text = path.read_text(encoding="utf-8", errors="ignore")
        return self.text

    def _pdf(self, path: Path) -> str:
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(path))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            print(f"PDF parse error: {e}")
            return ""

    def _docx(self, path: Path) -> str:
        try:
            from docx import Document

            doc = Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            print(f"DOCX parse error: {e}")
            return ""

    @property
    def keywords(self) -> Set[str]:
        import re

        tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9\+\#\.]{1,}", self.text.lower())
        stop = {
            "the",
            "and",
            "for",
            "with",
            "that",
            "this",
            "from",
            "have",
            "been",
            "will",
            "are",
            "was",
            "were",
            "you",
            "your",
            "our",
            "all",
            "any",
            "can",
            "has",
            "had",
            "not",
            "but",
            "about",
            "using",
            "work",
            "experience",
            "their",
            "them",
        }
        result: Set[str] = set()
        for t in tokens:
            t_clean = t.rstrip(".")
            if t_clean not in stop and len(t_clean) > 2:
                result.add(t_clean)
        return result
