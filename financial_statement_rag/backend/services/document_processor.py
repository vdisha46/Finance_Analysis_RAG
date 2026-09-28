import logging
from pathlib import Path
from typing import Any

import pandas as pd
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process uploaded financial documents from PDF, CSV, XLSX, and TXT."""

    @staticmethod
    def extract_text(file_path: str | Path) -> str:
        path = Path(file_path)
        suffix = path.suffix.lower()

        try:
            if suffix == ".pdf":
                reader = PdfReader(str(path))
                pages = []
                for page in reader.pages:
                    pages.append(page.extract_text() or "")
                return "\n".join(pages)
            if suffix in {".csv", ".txt"}:
                return path.read_text(encoding="utf-8", errors="ignore")
            if suffix in {".xlsx", ".xls"}:
                df = pd.read_excel(path)
                return df.to_markdown(index=False)
            return ""
        except Exception as exc:  # pragma: no cover - defensive handling
            logger.exception("Failed to extract text from %s", path)
            raise ValueError(f"Unable to process document: {exc}") from exc

    @staticmethod
    def parse_financial_rows(file_path: str | Path) -> list[dict[str, Any]]:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".csv":
            df = pd.read_csv(path)
            return df.to_dict(orient="records")
        if suffix in {".xlsx", ".xls"}:
            df = pd.read_excel(path)
            return df.to_dict(orient="records")
        return []
