"""Conditional routes and bounded loops: Nimbus Tier 4 lesson.

Run: uv run python modules/17_graphs/examples/03_conditional_budget.py --mock
Expected: Lesson complete. Mock fixtures cost $0; Ollama has no API fee.
Live inference uses configured rates and bounded calls. AWS resources created: none.
"""

from common.coordination import report
from common.graph_lessons import bounded_loop
from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.trip_graph import run_group_trip


def main() -> None:
    _, cfg = lesson_settings()
    result, state = run_group_trip(cfg, budget_cents=1)
    print("Within budget:", state["within_budget"])
    report(result, cfg)
    # KEY IDEA: a retry edge needs an execution ceiling and a deadline.
    graph, attempts = bounded_loop(maximum=3)
    result = graph("Revise an impossible budget")
    print("Revision attempts:", attempts["attempts"])
    report(result, cfg)
    complete()


if __name__ == "__main__":
    run_cli(main)
