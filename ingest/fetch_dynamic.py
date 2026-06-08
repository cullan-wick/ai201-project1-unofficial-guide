"""Headless-browser fetcher for JavaScript-rendered pages.

Used as a fallback when the lightweight `requests` path returns too little
text (client-rendered SPAs) and as a best-effort attempt at anti-bot-blocked
endpoints like Reddit. Reuses `html_to_markdown` so output matches the static
fetcher exactly.
"""

import json

from playwright.sync_api import sync_playwright

from ingest.fetch_static import USER_AGENT, html_to_markdown

NAV_TIMEOUT = 30_000   # ms
SETTLE_MS = 2_500      # extra wait after network idle for late hydration


def fetch_dynamic(url: str) -> str:
    """Render a page in headless Chromium and return cleaned markdown.

    Raises on navigation failure so the orchestrator can log and continue.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(user_agent=USER_AGENT)
            page.set_default_timeout(NAV_TIMEOUT)
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(SETTLE_MS)
            html = page.content()
        finally:
            browser.close()
    return html_to_markdown(html)


def fetch_json_dynamic(url: str) -> dict | list:
    """Load a JSON endpoint in headless Chromium and parse the response body.

    A real browser session can slip past simple anti-bot blocks (e.g. Reddit's
    403 on raw requests). Reddit serves the .json payload as the document body,
    which we read via `innerText` and parse.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(user_agent=USER_AGENT)
            page.set_default_timeout(NAV_TIMEOUT)
            page.goto(url, wait_until="domcontentloaded")
            body = page.eval_on_selector("body", "el => el.innerText")
        finally:
            browser.close()
    return json.loads(body)
