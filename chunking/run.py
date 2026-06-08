"""Chunking orchestrator.

Usage:
    python -m chunking.run

Reads every ingested document in documents/*.md, splits the body into
retrieval-sized chunks with chunking.splitter, and writes one JSON record per
chunk to documents/_chunks.jsonl. Each record carries the source's provenance
metadata so the embedding and generation stages can attribute answers.
"""

import json
from pathlib import Path

import yaml

from chunking.splitter import chunk_text, CHUNK_SIZE, OVERLAP

DOCS_DIR = Path("documents")
CHUNKS_FILE = DOCS_DIR / "_chunks.jsonl"

# Metadata fields copied from each document's frontmatter onto every chunk.
META_FIELDS = ("id", "source", "type", "category", "url")


def parse_document(path: Path) -> tuple[dict, str]:
    """Split a .md file into (frontmatter dict, body). Tolerates no frontmatter."""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            meta = yaml.safe_load(parts[1]) or {}
            return meta, parts[2].strip()
    return {}, text.strip()


def iter_documents() -> list[Path]:
    """All ingested docs, skipping helper files (_manifest.json, _raw, etc.)."""
    return sorted(p for p in DOCS_DIR.glob("*.md") if not p.name.startswith("_"))


def main() -> None:
    records: list[dict] = []
    per_doc: list[tuple[str, int]] = []

    for path in iter_documents():
        meta, body = parse_document(path)
        chunks = chunk_text(body)
        per_doc.append((path.stem, len(chunks)))
        base = {k: meta.get(k) for k in META_FIELDS}
        for i, chunk in enumerate(chunks):
            records.append({
                "chunk_id": f"{path.stem}::{i}",
                "doc_slug": path.stem,
                "chunk_index": i,
                "text": chunk,
                "char_len": len(chunk),
                **base,
            })

    with CHUNKS_FILE.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    sizes = [r["char_len"] for r in records]
    avg = sum(sizes) // len(sizes) if sizes else 0
    print("=" * 60)
    print(f"  Documents chunked : {len(per_doc)}")
    print(f"  Total chunks      : {len(records)}")
    print(f"  Chunk size target : {CHUNK_SIZE} chars (~512 tokens), {OVERLAP} overlap")
    print(f"  Avg chunk size    : {avg} chars   (min {min(sizes, default=0)}, "
          f"max {max(sizes, default=0)})")
    print(f"  Output            : {CHUNKS_FILE}")
    print("-" * 60)
    for slug, n in sorted(per_doc, key=lambda x: -x[1]):
        print(f"    {n:>3} chunks  {slug}")
    print("=" * 60)


if __name__ == "__main__":
    main()
