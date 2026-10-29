"""Rerank a candidate pool locally, then inspect the optional Bedrock contract.

Run: uv run python modules/08_advanced_rag/examples/03_reranking.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

from common.aws_retrieval import bedrock_rerank
from common.lessons import complete, lesson_settings
from common.pretty import console, run_cli
from common.retrieval import lexical_search, load_chunks, rerank


def main() -> None:
    args, cfg = lesson_settings()
    query = "approved refund timing"
    candidates = lexical_search(load_chunks(), query, k=5)
    # KEY IDEA: reranking cannot recover a document absent from the candidate pool.
    console.print("Local heuristic:", [c.id for c in rerank(query, candidates)])
    console.print(
        "Bedrock rerank:", bedrock_rerank(query, [c.text for c in candidates], mock=args.mock)
    )
    complete()


if __name__ == "__main__":
    run_cli(main)
