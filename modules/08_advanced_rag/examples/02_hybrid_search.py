"""Fuse BM25 and vector rankings without adding incomparable raw scores.

Run: uv run --group rag python modules/08_advanced_rag/examples/02_hybrid_search.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

from common.lessons import complete, lesson_settings
from common.models import get_embeddings
from common.pretty import console, run_cli
from common.retrieval import hybrid_search, lexical_search, load_chunks


def main() -> None:
    args, cfg = lesson_settings()
    chunks = load_chunks()
    query = "full cancellation refund conditions"
    console.print("Lexical:", [c.id for c in lexical_search(chunks, query)])
    # KEY IDEA: reciprocal rank fusion combines ranks, then deduplicates by stable ID.
    console.print(
        "Hybrid:",
        [c.record() for c in hybrid_search(chunks, query, get_embeddings(mock=args.mock))],
    )
    complete()


if __name__ == "__main__":
    run_cli(main)
