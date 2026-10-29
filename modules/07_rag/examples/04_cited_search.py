"""Let the agent search, then validate its citations against retrieved chunks.

Run: uv run python modules/07_rag/examples/04_cited_search.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

from common.lessons import complete, lesson_settings
from common.pretty import console, run_cli
from common.rag_agent import answer_policy
from common.retrieval import load_chunks


def main() -> None:
    args, cfg = lesson_settings()
    # KEY IDEA: source/quote validation is application code, not a promise in the prompt.
    result, evidence = answer_policy(cfg, "approved refund timing", load_chunks(pdf=True))
    console.print(result.structured_output.model_dump())
    console.print("Retrieved chunks:", len(evidence))
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
