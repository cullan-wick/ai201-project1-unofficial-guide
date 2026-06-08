"""Run the 5 evaluation questions from planning.md through the full pipeline.

Usage:
    python -m rag.evaluate

Prints each question, the system's grounded answer, the expected answer, and
the sources retrieved — the raw material for the README Evaluation Report.
"""

from rag.generate import answer

# The 5 test questions and expected answers, verbatim from planning.md.
EVAL = [
    ("If a student at UW-Madison is doing self-guided research and discovers something "
     "that could be monetizable and wants to turn it into a company, what should they do?",
     "Start with the Tech Entrepreneurship Office (TEO), the campus bridge for turning "
     "research into a startup (commercial evaluation, IP/tech-transfer, investor and "
     "mentor connections); disclose any invention to WARF for IP/licensing. Use the Tech "
     "Exploration Lab for prototyping and Transcend UW for mentorship and pitch funding."),
    ("What does Jon Eckhardt's report identify as the primary ecosystem challenge "
     "and what action item does it recommend?",
     "Systemic fragmentation across campus silos. It recommends creating a "
     "centralized, unified Wisconsin Entrepreneurship Hub."),
    ("What specific service limits or prerequisites does the Law & Entrepreneurship "
     "Clinic establish for free student legal services?",
     "Startups must clear an intake vetting showing they cannot afford private "
     "counsel and offer economic/operational value to WI."),
    ("I am a student at UW-Madison who likes venture capital and want to join an "
     "entrepreneurship club. What should I join?",
     "BadgerVC — a student-led org that makes venture capital accessible to "
     "undergraduates through speaker events and workshops. For hands-on investing, also "
     "consider StratoVC, a student-run venture fund that makes real investments."),
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
