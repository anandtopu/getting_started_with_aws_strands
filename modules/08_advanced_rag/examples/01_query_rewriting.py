"""Request bounded query rewrites, merge searches and deduplicate chunk IDs.

Run: uv run python modules/08_advanced_rag/examples/01_query_rewriting.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

from pydantic import BaseModel, Field
from strands import Agent

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli
from common.retrieval import lexical_search, load_chunks
from common.testing import tool_message


class Queries(BaseModel):
    queries: list[str] = Field(min_length=1, max_length=3)


def main() -> None:
    args, cfg = lesson_settings()
    agent = Agent(
        model=get_model(
            cfg,
            responses=[
                tool_message(
                    "Queries",
                    {"queries": ["refund approval threshold", "refund approval expiration"]},
                )
            ],
        ),
        structured_output_model=Queries,
        callback_handler=None,
        retry_strategy=None,
    )
    result = agent(
        "Rewrite: Who approves a refund and when does approval expire? "
        "Produce at most three short searches.",
        limits={"turns": 2},
    )
    if result.structured_output is None:
        raise ValueError("No queries within the turn budget")
    # KEY IDEA: cap both query count and per-query hits before merging evidence.
    hits = {}
    for query in result.structured_output.queries:
        for chunk in lexical_search(load_chunks(), query, k=2):
            hits[chunk.id] = chunk
    console.print("Unique evidence:", [c.record() for c in hits.values()])
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
