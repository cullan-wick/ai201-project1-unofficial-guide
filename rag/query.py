"""Interactive query interface for The Unofficial Guide.

Usage:
    python -m rag.query                 # interactive prompt loop
    python -m rag.query "your question" # single-shot answer

Loads the model on first query (a few seconds), then answers grounded in the
retrieved sources and prints which sources were available.
"""

import sys

from rag.generate import answer


def show(result: dict) -> None:
    print("\n" + result["answer"] + "\n")
    print("Sources retrieved:")
    for i, c in enumerate(result["chunks"], start=1):
        sim = 1 - c["distance"]  # cosine distance -> similarity
        print(f"  [{i}] {c['source']}  (sim {sim:.2f})  {c['url']}")
    print()


def main() -> None:
    if len(sys.argv) > 1:
        show(answer(" ".join(sys.argv[1:])))
        return

    print("The Unofficial Guide — UW-Madison startup ecosystem")
    print("Ask a question (Ctrl-C or empty line to quit).\n")
    try:
        while True:
            q = input("> ").strip()
            if not q:
                break
            show(answer(q))
    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == "__main__":
    main()
