"""Download a PDF and extract its text page by page with pdfplumber."""

import os
import tempfile
from pathlib import Path

import pdfplumber
import requests

from ingest.fetch_static import USER_AGENT, TIMEOUT

RAW_DIR = Path("documents/_raw")


def _download(url: str, dest: Path | str) -> None:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
    resp.raise_for_status()
    Path(dest).write_bytes(resp.content)


def _extract(path: Path | str) -> str:
    """Extract text from a local PDF, page by page."""
    pages: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text.strip())
    return "\n\n".join(pages).strip()


def fetch_pdf(url: str, slug: str) -> str:
    """Download to documents/_raw/<slug>.pdf and return extracted text.

    Used for sources registered directly as PDFs (keeps a persistent copy).
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = RAW_DIR / f"{slug}.pdf"
    _download(url, pdf_path)
    return _extract(pdf_path)


def fetch_pdf_text(url: str) -> str:
    """Download a PDF to a temp file and return its text (no persistent copy).

    Used by the crawler when it discovers a linked PDF mid-crawl.
    """
    fd, tmp = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    try:
        _download(url, tmp)
        return _extract(tmp)
    finally:
        os.remove(tmp)
