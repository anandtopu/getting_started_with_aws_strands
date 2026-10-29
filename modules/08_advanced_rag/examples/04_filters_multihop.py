"""Bound a two-hop policy lookup and keep metadata filters explicit.

Run: uv run python modules/08_advanced_rag/examples/04_filters_multihop.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

from strands import Agent, tool

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli
from common.retrieval import lexical_search, load_chunks
from common.testing import tool_message


def main() -> None:
    args, cfg = lesson_settings()
    chunks = load_chunks()
    # KEY IDEA: a second hop follows a policy reference, not an unbounded model loop.
    first = lexical_search(chunks, "full refund exception", k=2, topic="refund")
    next_query = (
        "full refund cancellation 24 hours 7 days"
        if any("POL-CAN-001" in c.text for c in first)
        else "cancellation"
    )
    second = lexical_search(chunks, next_query, k=2, topic="cancellation")
    console.print("Hop 1:", [c.record() for c in first])
    console.print("Hop 2:", [c.record() for c in second])
    calls = 0

    @tool
    def search_policy_topic(query: str, topic: str) -> list[dict]:
        """Search a bounded policy topic.

        Args:
            query: The question or policy cross-reference.
            topic: Either refund or cancellation for this lab.
        """
        nonlocal calls
        calls += 1
        if calls > 2 or topic not in {"refund", "cancellation"}:
            raise ValueError("Only two searches of approved topics are allowed")
        return [c.record() for c in lexical_search(chunks, query, k=2, topic=topic)]

    agent = Agent(
        model=get_model(
            cfg,
            responses=[
                tool_message(
                    "search_policy_topic", {"query": "full refund exception", "topic": "refund"}
                ),
                tool_message(
                    "search_policy_topic", {"query": next_query, "topic": "cancellation"}, "hop2"
                ),
                "Both the 24-hour booking window and the 7-day departure condition apply.",
            ],
        ),
        tools=[search_policy_topic],
        callback_handler=None,
        retry_strategy=None,
        system_prompt=(
            "Search refund policy, then follow its cancellation reference. "
            "Use at most two searches."
        ),
    )
    result = agent("What conditions determine a full refund?", limits={"turns": 3})
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
