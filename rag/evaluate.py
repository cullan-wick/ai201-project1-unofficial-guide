"""Run the 5 evaluation questions from planning.md through the full pipeline.

Usage:
    python -m rag.evaluate

Prints each question, the system's grounded answer, the expected answer, and
the sources retrieved — the raw material for the README Evaluation Report.
"""

from rag.generate import answer

# The 5 test questions and expected answers, verbatim from planning.md.
EVAL = [
    ("If a student builds a software MVP in their dorm using personal devices and "
     "campus Wi-Fi, does WARF claim intellectual property?",
     "No. Standard dorm use and Wi-Fi do not constitute 'substantial university "
     "resources.' IP remains fully owned by the student."),
    ("What does Jon Eckhardt's report identify as the primary ecosystem challenge "
     "and what action item does it recommend?",
     "Systemic fragmentation across campus silos. It recommends creating a "
     "centralized, unified Wisconsin Entrepreneurship Hub."),
    ("What specific service limits or prerequisites does the Law & Entrepreneurship "
     "Clinic establish for free student legal services?",
     "Startups must clear an intake vetting showing they cannot afford private "
     "counsel and offer economic/operational value to WI."),
    ("Under what specific academic course framework can a student qualify to receive "
     "equity investments from the Weinert Venture Funds?",
     "Students must be enrolled in the WAVE Practicum (Wisconsin Applied Ventures in "
     "Entrepreneurship) course at the Weinert Center."),
    ("What specific off-campus Madison alternative provides heavy tooling/CNC "
     "machinery when Grainger Engineering Makerspace is closed?",
     "Sector67. A non-profit community hackerspace operating outside university "
     "hours, calendar restrictions, and enrollment status."),
]


def main() -> None:
    for i, (question, expected) in enumerate(EVAL, start=1):
        result = answer(question)
        print("=" * 78)
        print(f"Q{i}: {question}")
        print("-" * 78)
        print(f"SYSTEM ANSWER:\n{result['answer']}\n")
        print(f"EXPECTED:\n{expected}\n")
        print("RETRIEVED:")
        for j, c in enumerate(result["chunks"], start=1):
            print(f"  [{j}] {c['source']}  (sim {1 - c['distance']:.2f})")
    print("=" * 78)


if __name__ == "__main__":
    main()
