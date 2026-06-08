"""Retrieval over the ChromaDB vector store.

Embeds a query with the same local bge-m3 model used at index time, then runs a
cosine similarity search and returns the top-k chunks with their provenance.
"""

import chromadb

from vectorstore import CHROMA_DIR, COLLECTION
from vectorstore.embedder import embed_query

TOP_K = 8
PER_SOURCE_CAP = 2     # max chunks from one source in the final top-k
CANDIDATE_POOL = 24    # over-fetch, then diversify down to TOP_K

_collection = None


def get_collection():
    """Lazily open the persistent collection (raises if it hasn't been built)."""
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        try:
            _collection = client.get_collection(COLLECTION)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(
                f"Collection '{COLLECTION}' not found in {CHROMA_DIR}/. "
                f"Run `python -m vectorstore.build` first."
            ) from exc
    return _collection


def retrieve(query: str, k: int = TOP_K, per_source_cap: int = PER_SOURCE_CAP) -> list[dict]:
    """Return the k most similar chunks, diversified across sources.

    Over-fetches a candidate pool, then greedily keeps chunks in similarity order
    while allowing at most `per_source_cap` chunks per source — preventing a
    high-page-count source (e.g. a 50-page crawl) from flooding the top-k and
    burying small but on-target sources. If the cap leaves fewer than k chunks,
    the remaining slots are backfilled from the next-best leftovers.
    """
    res = get_collection().query(
        query_embeddings=[embed_query(query)], n_results=max(CANDIDATE_POOL, k)
    )
    candidates = [
        {"text": doc, "distance": dist, **meta}
        for doc, dist, meta in zip(res["documents"][0], res["distances"][0], res["metadatas"][0])
    ]

    chosen, leftovers, per_source = [], [], {}
    for c in candidates:  # already in ascending-distance (best-first) order
        src = c.get("source", "")
        if per_source.get(src, 0) < per_source_cap:
            chosen.append(c)
            per_source[src] = per_source.get(src, 0) + 1
        else:
            leftovers.append(c)
        if len(chosen) == k:
            return chosen

    # Cap left us short of k — backfill with the best remaining chunks.
    chosen.extend(leftovers[: k - len(chosen)])
    return chosen
