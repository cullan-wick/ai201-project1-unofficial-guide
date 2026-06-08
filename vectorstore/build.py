"""Build the ChromaDB vector store from chunked documents.

Usage:
    python -m vectorstore.build

Reads documents/_chunks.jsonl, embeds every chunk with bge-m3, and writes them
into a persistent ChromaDB collection (cosine space) with full provenance
metadata. Re-runnable: the collection is dropped and rebuilt each time.
"""

import json
from pathlib import Path

import chromadb

from vectorstore import CHROMA_DIR, COLLECTION
from vectorstore.embedder import embed

CHUNKS_FILE = Path("documents/_chunks.jsonl")
META_FIELDS = ("doc_slug", "chunk_index", "source", "type", "category", "url")


def load_chunks() -> list[dict]:
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(f"{CHUNKS_FILE} not found — run `python -m chunking.run` first.")
    return [json.loads(line) for line in CHUNKS_FILE.open(encoding="utf-8")]


def main() -> None:
    chunks = load_chunks()
    print(f"[build] {len(chunks)} chunks loaded from {CHUNKS_FILE}")

    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    # Chroma metadata values must be scalars (no None) — coerce missing to "".
    metadatas = [{k: (c.get(k) if c.get(k) is not None else "") for k in META_FIELDS}
                 for c in chunks]

    print("[build] embedding with bge-m3 (first run downloads the model) ...")
    vectors = embed(texts, show_progress=True)

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    # Drop any prior collection so rebuilds are clean/idempotent.
    if COLLECTION in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION)
    collection = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})

    collection.add(ids=ids, embeddings=vectors, documents=texts, metadatas=metadatas)

    print("=" * 60)
    print(f"  Vectors stored : {collection.count()}")
    print(f"  Collection     : {COLLECTION} (cosine)")
    print(f"  Persisted at   : {CHROMA_DIR}/")
    print(f"  Vector dim     : {len(vectors[0])}")
    print("=" * 60)


if __name__ == "__main__":
    main()
