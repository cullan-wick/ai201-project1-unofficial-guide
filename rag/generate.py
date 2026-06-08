"""Grounded generation over retrieved context using Groq.

Retrieves top-k chunks, formats them as a numbered, source-attributed context
block, and asks openai/gpt-oss-120b to answer strictly from that context. The
system prompt forbids outside knowledge and requires inline [n] citations, so
answers stay grounded and traceable to a source.
"""

import os

from dotenv import load_dotenv
from groq import Groq

from rag.retriever import retrieve, TOP_K

MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """You are The Unofficial Guide to the UW-Madison startup ecosystem.
Answer the user's question using ONLY the numbered SOURCES provided below.

Rules:
- Use only facts found in the SOURCES. Do not add outside knowledge or assumptions.
- Cite the source number(s) you used inline, like [1] or [2][3], right after the claim.
- If the SOURCES do not contain the answer, say exactly: "I don't have information on that in my sources." Do not guess.
- Be concise and practical. Prefer specifics (program names, eligibility, locations) over vague summaries.
"""

_client: Groq | None = None


def get_client() -> Groq:
    global _client
    if _client is None:
        load_dotenv()
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY not set. Add it to your .env file.")
        _client = Groq(api_key=key)
    return _client


def format_context(chunks: list[dict]) -> str:
    """Render retrieved chunks as a numbered, source-attributed context block."""
    blocks = []
    for i, c in enumerate(chunks, start=1):
        blocks.append(f"[{i}] Source: {c['source']} ({c['url']})\n{c['text']}")
    return "\n\n".join(blocks)


def answer(query: str, k: int = TOP_K, temperature: float = 0.0) -> dict:
    """Run the full RAG turn. Returns {answer, chunks, sources}."""
    chunks = retrieve(query, k)
    context = format_context(chunks)
    user_msg = f"SOURCES:\n{context}\n\nQUESTION: {query}"

    resp = get_client().chat.completions.create(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )
    text = resp.choices[0].message.content.strip()

    # De-duplicate the sources actually available to the model, preserving order.
    seen, sources = set(), []
    for c in chunks:
        key = (c["source"], c["url"])
        if key not in seen:
            seen.add(key)
            sources.append({"source": c["source"], "url": c["url"]})
    return {"answer": text, "chunks": chunks, "sources": sources}
