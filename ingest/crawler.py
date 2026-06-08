"""Breadth-first, scope-limited web crawler.

Starting from a seed URL, follows in-scope links up to a depth and page cap,
returning each page's content in crawl order. Reuses the existing fetchers:
`fetch_static_with_links` for HTML (with a Playwright fallback for thin SPA
shells) and `fetch_pdf_text` for linked PDFs.

Scope (what keeps it bounded):
  - same host as the seed
  - path under `prefix` (defaults to the seed's directory; "" = whole host)
  - max_depth link-hops from the seed, and a hard max_pages ceiling
  - skips non-HTTP schemes, asset/binary extensions, and common crawler traps
  - honors robots.txt by default
"""

import time
import urllib.robotparser
from collections import deque
from urllib.parse import urldefrag, urlparse

from ingest.fetch_static import USER_AGENT, fetch_static_with_links
from ingest.fetch_pdf import fetch_pdf_text

THIN_WORDS = 50  # below this, retry the page with a headless browser
SKIP_EXT = (
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico", ".css", ".js",
    ".zip", ".gz", ".mp4", ".mov", ".mp3", ".doc", ".docx", ".xls", ".xlsx",
    ".ppt", ".pptx", ".ics", ".rss", ".xml",
)
TRAP_SUBSTRINGS = ("/tag/", "/category/", "/author/", "replytocom", "/page/",
                   "/feed", "?share=", "/calendar")


def _norm(url: str) -> str:
    """Drop the fragment and trailing slash so URL variants dedupe."""
    url, _ = urldefrag(url)
    return url.rstrip("/") or url


def _default_prefix(seed: str) -> str:
    """Seed's directory path; '' (whole host) when the seed is the site root."""
    path = urlparse(seed).path
    prefix = path if path.endswith("/") else path.rsplit("/", 1)[0] + "/"
    return "" if prefix == "/" else prefix


def _allowed(url: str, host: str, prefix: str) -> bool:
    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        return False
    if p.netloc != host:
        return False
    if prefix and not p.path.startswith(prefix):
        return False
    if p.path.lower().endswith(SKIP_EXT):
        return False
    if any(t in url.lower() for t in TRAP_SUBSTRINGS):
        return False
    return True


def _is_pdf_url(url: str) -> bool:
    return urlparse(url).path.lower().endswith(".pdf")


def _fetch_page(url: str) -> dict | None:
    """Fetch one page. Returns {url, kind, content, links} or None on failure."""
    if _is_pdf_url(url):
        return {"url": url, "kind": "pdf", "content": fetch_pdf_text(url), "links": []}
    try:
        md, links = fetch_static_with_links(url)
    except ValueError:  # server actually returned a PDF
        return {"url": url, "kind": "pdf", "content": fetch_pdf_text(url), "links": []}
    if len(md.split()) < THIN_WORDS:  # JS-rendered shell -> headless browser
        try:
            from ingest.fetch_dynamic import fetch_dynamic
            rendered = fetch_dynamic(url)
            if len(rendered.split()) > len(md.split()):
                md = rendered
        except Exception:  # noqa: BLE001 - keep the static body
            pass
    return {"url": url, "kind": "html", "content": md, "links": links}


def crawl(seed: str, *, max_depth: int = 3, max_pages: int = 50,
          prefix: str | None = None, respect_robots: bool = True,
          delay: float = 0.7) -> list[dict]:
    """Crawl from `seed` and return a list of {url, kind, content} pages."""
    host = urlparse(seed).netloc
    if prefix is None:
        prefix = _default_prefix(seed)

    robots = None
    if respect_robots:
        robots = urllib.robotparser.RobotFileParser()
        try:
            robots.set_url(f"https://{host}/robots.txt")
            robots.read()
        except Exception:  # noqa: BLE001 - no robots -> allow
            robots = None

    def can_fetch(url: str) -> bool:
        return robots.can_fetch(USER_AGENT, url) if robots else True

    visited: set[str] = set()
    queue: deque[tuple[str, int]] = deque([(_norm(seed), 0)])
    pages: list[dict] = []

    while queue and len(pages) < max_pages:
        url, depth = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        if not can_fetch(url):
            continue
        try:
            page = _fetch_page(url)
        except Exception:  # noqa: BLE001 - skip a broken page, keep crawling
            continue
        if not page or not page["content"].strip():
            continue
        pages.append({"url": page["url"], "kind": page["kind"], "content": page["content"]})

        if depth < max_depth:
            for link in page["links"]:
                n = _norm(link)
                if n not in visited and _allowed(n, host, prefix):
                    queue.append((n, depth + 1))
        time.sleep(delay)

    return pages
