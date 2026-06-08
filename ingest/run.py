"""Ingestion orchestrator.

Usage:
    python -m ingest.run

Dispatches each registered source to the right fetcher, writes one clean
markdown file per document into documents/ (with YAML frontmatter for
provenance), and records a documents/_manifest.json summary. Failures are
logged but never abort the run.
"""

import json
from datetime import date
from pathlib import Path

import yaml

from ingest.sources import SOURCES, Source
from ingest.fetch_static import fetch_static
from ingest.fetch_pdf import fetch_pdf
from ingest.crawler import crawl

DOCS_DIR = Path("documents")
TRANSCRIPTS_DIR = DOCS_DIR / "transcripts"
MANIFEST = DOCS_DIR / "_manifest.json"
DROP_SUFFIXES = (".txt", ".vtt", ".md")

# Crawl depth/page caps applied to every static_html source.
CRAWL_MAX_DEPTH = 3
CRAWL_MAX_PAGES = 50


def write_document(slug: str, meta: dict, body: str) -> int:
    """Write documents/<slug>.md with YAML frontmatter. Returns word count."""
    word_count = len(body.split())
    meta = {**meta, "word_count": word_count}
    front = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    (DOCS_DIR / f"{slug}.md").write_text(
        f"---\n{front}\n---\n\n{body}\n", encoding="utf-8"
    )
    return word_count


def base_meta(src: Source, **overrides) -> dict:
    meta = {
        "id": src.id,
        "source": src.name,
        "type": src.type,
        "category": src.category,
        "url": src.url,
        "fetched_at": date.today().isoformat(),
    }
    meta.update(overrides)
    return meta


def handle_static(src: Source, results: list[dict]) -> None:
    """Crawl the source (multi-page) and concatenate pages into one document."""
    pages = crawl(src.url, max_depth=CRAWL_MAX_DEPTH, max_pages=CRAWL_MAX_PAGES,
                  prefix=src.crawl_prefix)

    # Fall back to a single fetch if the crawl yielded nothing.
    if not pages:
        try:
            pages = [{"url": src.url, "kind": "html", "content": fetch_static(src.url)}]
        except ValueError:
            pages = [{"url": src.url, "kind": "pdf", "content": fetch_pdf(src.url, src.slug)}]

    # One doc per source: each page delimited by a header carrying its URL,
    # so the exact page stays attributable inside the concatenated body.
    body = "\n\n".join(f"## [page] {p['url']}\n\n{p['content']}" for p in pages).strip()
    print(f"      crawled {len(pages)} page(s)", flush=True)

    wc = write_document(src.slug, base_meta(src, method="crawl", pages_crawled=len(pages)), body)
    results.append({"id": src.id, "slug": src.slug, "status": "ok",
                    "word_count": wc, "method": "crawl", "pages": len(pages), "url": src.url})


def handle_pdf(src: Source, results: list[dict]) -> None:
    body = fetch_pdf(src.url, src.slug)
    wc = write_document(src.slug, base_meta(src), body)
    results.append({"id": src.id, "slug": src.slug, "status": "ok",
                    "word_count": wc, "url": src.url})


def ingest_dropped_files(src: Source, folder: Path, results: list[dict], method: str) -> int:
    """Ingest hand-saved .txt/.vtt/.md files from a drop folder.

    Skips dotfiles, README, and `_`-prefixed helper files. Returns the count
    ingested so callers can decide whether to report a skip.
    """
    if not folder.exists():
        return 0
    files = sorted(
        p for p in folder.iterdir()
        if p.suffix.lower() in DROP_SUFFIXES
        and not p.stem.startswith(("_", "."))
        and p.stem.lower() != "readme"
    )
    for f in files:
        slug = f"{src.slug}-{f.stem}"
        body = f.read_text(encoding="utf-8", errors="ignore").strip()
        meta = base_meta(src, url=f"file://{f.name}", thread_title=f.stem, method=method)
        wc = write_document(slug, meta, body)
        results.append({"id": src.id, "slug": slug, "status": "ok",
                        "word_count": wc, "method": method, "url": f"file://{f.name}"})
    return len(files)


def handle_transcript(src: Source, results: list[dict]) -> None:
    """Ingest any files manually dropped into documents/transcripts/."""
    if ingest_dropped_files(src, TRANSCRIPTS_DIR, results, "transcript-manual") == 0:
        results.append({"id": src.id, "slug": src.slug, "status": "skipped",
                        "error": f"no files in {TRANSCRIPTS_DIR}/"})


DISPATCH = {
    "static_html": handle_static,
    "pdf": handle_pdf,
    "transcript": handle_transcript,
}


def main() -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    results: list[dict] = []

    for src in SOURCES:
        print(f"[{src.id:>2}] {src.type:<11} {src.name} ...", flush=True)
        handler = DISPATCH[src.type]
        try:
            handler(src, results)
        except Exception as exc:  # noqa: BLE001 - log and continue
            results.append({"id": src.id, "slug": src.slug, "status": "failed",
                            "url": src.url, "error": f"{type(exc).__name__}: {exc}"})
            print(f"      FAILED: {type(exc).__name__}: {exc}", flush=True)

    MANIFEST.write_text(json.dumps(results, indent=2), encoding="utf-8")

    ok = [r for r in results if r["status"] == "ok"]
    failed = [r for r in results if r["status"] == "failed"]
    skipped = [r for r in results if r["status"] == "skipped"]
    total_words = sum(r.get("word_count", 0) for r in ok)

    print("\n" + "=" * 60)
    print(f"  Documents written : {len(ok)}")
    print(f"  Failed            : {len(failed)}")
    print(f"  Skipped           : {len(skipped)}")
    print(f"  Total words       : {total_words:,}")
    print(f"  Manifest          : {MANIFEST}")
    if failed:
        print("\n  Failures:")
        for r in failed:
            print(f"    - [{r['id']}] {r['slug']}: {r.get('error')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
