"""Fetch a static HTML page and return clean markdown.

Strips boilerplate (nav/header/footer/scripts) and converts the remaining
content to markdown so the chunking stage can key off real headings.
"""

import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 UnofficialGuideBot/1.0"
)
TIMEOUT = 15
BOILERPLATE_TAGS = ["script", "style", "noscript", "nav", "header", "footer", "aside", "form"]


def _get(url: str, retries: int = 2) -> requests.Response:
    """GET with a real User-Agent and simple linear backoff."""
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise last_exc  # type: ignore[misc]


def is_pdf_response(resp: requests.Response) -> bool:
    """True when the server actually served a PDF (some .pdf-less URLs do)."""
    ctype = resp.headers.get("Content-Type", "").lower()
    return "application/pdf" in ctype or resp.content[:5] == b"%PDF-"


def html_to_markdown(html: str) -> str:
    """Strip boilerplate from an HTML string and return cleaned markdown.

    Shared by the static fetcher and the Playwright dynamic fetcher so both
    produce identically-formatted output.
    """
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(BOILERPLATE_TAGS):
        tag.decompose()

    # Prefer <main>/<article> when present, else fall back to <body>.
    root = soup.find("main") or soup.find("article") or soup.body or soup
    md = markdownify(str(root), heading_style="ATX", strip=["a"])

    # Collapse runs of blank lines left behind by stripped boilerplate.
    lines = [ln.rstrip() for ln in md.splitlines()]
    cleaned: list[str] = []
    blank = 0
    for ln in lines:
        if ln.strip():
            blank = 0
            cleaned.append(ln)
        else:
            blank += 1
            if blank <= 1:
                cleaned.append("")
    return "\n".join(cleaned).strip()


def fetch_static(url: str) -> str:
    """Fetch an HTML page and return cleaned markdown.

    Raises requests.RequestException on network failure (orchestrator logs and
    continues). Raises ValueError if the URL is actually a PDF so the caller can
    re-dispatch to the PDF fetcher.
    """
    resp = _get(url)
    if is_pdf_response(resp):
        raise ValueError("served_pdf")
    return html_to_markdown(resp.text)


def fetch_static_with_links(url: str) -> tuple[str, list[str]]:
    """Fetch a page once and return (cleaned markdown, absolute outgoing links).

    Links are extracted from the full page (including nav/menus, where section
    sub-page links usually live), while the markdown body uses the boilerplate-
    stripped content. Raises ValueError("served_pdf") if the URL is a PDF.
    """
    resp = _get(url)
    if is_pdf_response(resp):
        raise ValueError("served_pdf")
    html = resp.text
    soup = BeautifulSoup(html, "lxml")
    links = [urljoin(url, a["href"]) for a in soup.find_all("a", href=True)]
    return html_to_markdown(html), links
