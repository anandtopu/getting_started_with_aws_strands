"""Parallel branches with fan-in: Nimbus Tier 4 lesson.

Run: uv run python modules/17_graphs/examples/02_parallel_search.py --mock
Expected: Lesson complete. Mock fixtures cost $0; Ollama has no API fee.
Live inference uses configured rates and bounded calls. AWS resources created: none.
"""

from common.coordination import report
from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.trip_graph import group_trip_graph


def main() -> None:
    _, cfg = lesson_settings()
    graph, state, request = group_trip_graph(cfg, budget_cents=1, search_delay=0.05)
    result = graph(request.model_dump_json())
    flight, hotel = state["intervals"]["flight"], state["intervals"]["hotel"]
    # KEY IDEA: overlap proves concurrency; the budget waits for both branches.
    print("Search intervals overlap:", max(flight[0], hotel[0]) < min(flight[1], hotel[1]))
    print("Joined quote:", state["review"].quote.model_dump())
    report(result, cfg)
    complete()


if __name__ == "__main__":
    run_cli(main)
