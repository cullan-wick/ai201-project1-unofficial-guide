"""bge-m3 embedding wrapper, shared by the build script and retrieval.

Loads BAAI/bge-m3 once (lazy) and runs it locally. On Apple Silicon it uses the
MPS backend (the M3's unified memory makes the 1024-dim model fast on-device);
otherwise it falls back to CPU. Embeddings are L2-normalized so the ChromaDB
cosine space behaves like a dot product.
"""

from functools import lru_cache

MODEL_NAME = "BAAI/bge-m3"


def _pick_device() -> str:
    import torch
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


@lru_cache(maxsize=1)
def get_model():
    """Load and cache the SentenceTransformer model (first call downloads ~2.2GB)."""
    from sentence_transformers import SentenceTransformer
    device = _pick_device()
    print(f"[embedder] loading {MODEL_NAME} on {device} ...", flush=True)
    return SentenceTransformer(MODEL_NAME, device=device)


def embed(texts: list[str], batch_size: int = 16, show_progress: bool = False) -> list[list[float]]:
    """Embed a list of texts into normalized vectors."""
    model = get_model()
    vectors = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
    )
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    """Embed a single query string."""
    return embed([text])[0]
