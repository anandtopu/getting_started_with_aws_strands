"""Handoffs and shared context: Nimbus Tier 4 lesson.

Run: uv run python modules/16_swarms/examples/01_handoffs.py --mock
Expected: Lesson complete. Mock fixtures cost $0; Ollama has no API fee.
Live inference uses configured rates and bounded calls. AWS resources created: none.
"""

from common.coordination import report
from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.swarm_lessons import itinerary_swarm


def main() -> None:
    _, cfg = lesson_settings()
    swarm = itinerary_swarm(cfg)
    # KEY IDEA: the model selects handoff_to_agent; the runtime checks its limits.
    result = swarm("Design a public Porto itinerary. Do not book anything.")
    report(result, cfg)
    complete()


if __name__ == "__main__":
    run_cli(main)
