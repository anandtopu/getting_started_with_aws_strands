"""Inspect node outcomes: Nimbus Tier 4 lesson.

Run: uv run python modules/16_swarms/examples/03_swarm_results.py --mock
Expected: Lesson complete. Mock fixtures cost $0; Ollama has no API fee.
Live inference uses configured rates and bounded calls. AWS resources created: none.
"""

from common.coordination import report
from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.swarm_lessons import itinerary_swarm


def main() -> None:
    _, cfg = lesson_settings()
    for loop in (False, True):
        result = itinerary_swarm(cfg, loop=loop)("Plan a synthetic Porto draft")
        report(result, cfg)
        # KEY IDEA: inspect status and visited nodes before accepting reassuring prose.
        for name, node in result.results.items():
            print(name, node.status.value, str(node.result)[:250])
    complete()


if __name__ == "__main__":
    run_cli(main)
