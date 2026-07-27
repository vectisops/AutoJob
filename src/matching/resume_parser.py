from pathlib import Path
from typing import Optional


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
        elif suffix in (".docx", ".doc"):
            self.text = self._docx(path)
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
    def keywords(self) -> set[str]:
        import re
        tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9\+\#\.]{1,}", self.text.lower())
        stop = {"the", "and", "for", "with", "that", "this", "from", "have", "been", "will", "are", "was", "were", "you", "your", "our", "all", "any", "can", "has", "had", "not", "but"}
        return {t for t in tokens if t not in stop and len(t) > 2}
