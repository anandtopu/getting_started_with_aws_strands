"""Four-role itinerary team: Nimbus Tier 4 lesson.

Run: uv run python modules/16_swarms/examples/04_itinerary_team.py --mock
Expected: Lesson complete. Mock fixtures cost $0; Ollama has no API fee.
Live inference uses configured rates and bounded calls. AWS resources created: none.
"""

import json

from common.coordination import report
from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.swarm_lessons import itinerary_swarm
from common.trip_planning import TripRequest, catalog


def main() -> None:
    _, cfg = lesson_settings()
    request = TripRequest()
    evidence = {role: catalog(role, request) for role in ("flight", "hotel", "policy")}
    task = "Design a two-day Porto itinerary from this public evidence: " + json.dumps(evidence)
    result = itinerary_swarm(cfg)(task)
    report(result, cfg)
    print("Reviewer:", str(result.results.get("reviewer")))
    print("This creative handoff exercise does not authorize spending.")
    complete()


if __name__ == "__main__":
    run_cli(main)
