"""Markdown-aware recursive text splitter.

One unified strategy for the whole corpus. The original planning.md specced a
4-way asymmetric router, but after Reddit was excluded and no transcripts were
collected, only two archetypes remain (short web docs + one long PDF). A single
recursive splitter handles both cleanly.

Sizes are measured in characters as a cheap, deterministic proxy for tokens
(English averages ~4 chars/token), so a ~2000-char target ≈ ~500 tokens — well
within bge-m3's 8192-token ceiling. Splitting respects structure in priority
order: markdown headers, then paragraphs, then sentences, then words. Words are
never cut mid-token.
"""

import re

CHUNK_SIZE = 2000      # chars (~500 tokens)
OVERLAP = 300          # chars (~15%)

# Paragraph/section separators, highest-priority structural break first.
_HEADER_RE = re.compile(r"(?m)^(#{1,6} .*)$")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _split_blocks(text: str) -> list[str]:
    """Break text into structural blocks: heading lines and paragraphs."""
    # Keep markdown headings as their own boundary by inserting blank lines.
    text = _HEADER_RE.sub(r"\n\n\1\n", text)
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text)]
    return [b for b in blocks if b]


def _split_oversized(block: str, size: int) -> list[str]:
    """Split a block larger than `size` by sentences, then by words."""
    pieces: list[str] = []
    for sentence in _SENTENCE_RE.split(block):
        if len(sentence) <= size:
            pieces.append(sentence)
            continue
        # Sentence still too long: pack word by word.
        words, cur = sentence.split(), ""
        for w in words:
            if cur and len(cur) + 1 + len(w) > size:
                pieces.append(cur)
                cur = w
            else:
                cur = f"{cur} {w}".strip()
        if cur:
            pieces.append(cur)
    return pieces


def _tail_overlap(chunk: str, overlap: int) -> str:
    """Return the last ~`overlap` chars of `chunk`, snapped to a word boundary."""
    if overlap <= 0 or len(chunk) <= overlap:
        return chunk if overlap > 0 else ""
    tail = chunk[-overlap:]
    # Snap forward to the next space so we don't start mid-word.
    space = tail.find(" ")
    return tail[space + 1:] if space != -1 else tail


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    """Split `text` into overlapping, structure-aware chunks.

    Greedily packs structural blocks up to `chunk_size`; oversized blocks are
    broken on sentence then word boundaries. Each chunk after the first is
    prefixed with the tail of the previous one to preserve cross-boundary context.
    """
    text = text.strip()
    if not text:
        return []

    # Expand blocks, pre-splitting any that exceed the target size.
    units: list[str] = []
    for block in _split_blocks(text):
        units.extend(_split_oversized(block, chunk_size) if len(block) > chunk_size else [block])

    # Greedily pack units into chunks.
    chunks: list[str] = []
    cur = ""
    for unit in units:
        if cur and len(cur) + 2 + len(unit) > chunk_size:
            chunks.append(cur)
            cur = unit
        else:
            cur = f"{cur}\n\n{unit}".strip()
    if cur:
        chunks.append(cur)

    if overlap <= 0 or len(chunks) <= 1:
        return chunks

    # Prepend previous-chunk tail for context continuity.
    overlapped = [chunks[0]]
    for i in range(1, len(chunks)):
        tail = _tail_overlap(chunks[i - 1], overlap)
        overlapped.append(f"{tail}\n\n{chunks[i]}".strip() if tail else chunks[i])
    return overlapped
