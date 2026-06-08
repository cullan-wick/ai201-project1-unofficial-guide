"""Cross-encoder reranker.

The bi-encoder (bge-m3) scores the query and each chunk separately, which is fast
but coarse — and after the multi-page crawl it buries small high-signal sources.
A cross-encoder scores each (query, chunk) pair *together* for a much sharper
relevance judgment. Pattern: retrieve a wide pool with the bi-encoder, rerank it
here, then take the best.
"""

from functools import lru_cache

MODEL_NAME = "BAAI/bge-reranker-v2-m3"


def _pick_device() -> str:
    import torch
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


@lru_cache(maxsize=1)
def get_reranker():
    """Load and cache the CrossEncoder (first call downloads ~2.2GB)."""
    from sentence_transformers import CrossEncoder
    device = _pick_device()
    print(f"[reranker] loading {MODEL_NAME} on {device} ...", flush=True)
    return CrossEncoder(MODEL_NAME, device=device)


def rerank(query: str, candidates: list[dict]) -> list[dict]:
    """Return candidates re-sorted by cross-encoder relevance (best first).

    Each candidate dict gets a `rerank_score` added. Raw logits are used — only
    relative order matters for ranking.
    """
    if not candidates:
        return candidates
    model = get_reranker()
    scores = model.predict([(query, c["text"]) for c in candidates])
    for c, s in zip(candidates, scores):
        c["rerank_score"] = float(s)
    return sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)
