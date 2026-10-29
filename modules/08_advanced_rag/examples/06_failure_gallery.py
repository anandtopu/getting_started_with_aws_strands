"""Expose false citations, missing evidence and untrusted retrieved instructions.

Run: uv run python modules/08_advanced_rag/examples/06_failure_gallery.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

from common.data import data_path
from common.lessons import complete, lesson_settings
from common.pretty import console, run_cli
from common.rag_agent import PolicyAnswer, validate_citations
from common.retrieval import load_chunks


def main() -> None:
    args, cfg = lesson_settings()
    chunk = load_chunks()[0]
    bad = PolicyAnswer(
        answer="Every trip is free.",
        abstained=False,
        citations=[
            {
                "chunk_id": chunk.id,
                "source": chunk.source,
                "page": chunk.page,
                "quote": "Every trip is free.",
            }
        ],
    )
    try:
        validate_citations(bad, [chunk])
    except ValueError as exc:
        console.print("Rejected false citation:", str(exc))
    # KEY IDEA: quarantine poison; quote validation alone cannot stop injection.
    poisoned = data_path("security/poisoned_doc.md").read_text(encoding="utf-8")
    console.print("Untrusted document excluded from approved corpus:", len(poisoned), "characters")
    safe = PolicyAnswer(answer="I do not know from these sources.", abstained=True, citations=[])
    validate_citations(safe, [])
    console.print("Missing evidence:", safe.answer)
    complete()


if __name__ == "__main__":
    run_cli(main)
