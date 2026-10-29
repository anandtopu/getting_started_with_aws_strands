"""Minimum context and authoritative output validation: Nimbus Tier 4 lesson.

Run: uv run python modules/15_agents_as_tools/examples/02_context_boundaries.py --mock
Expected: Lesson complete. Mock fixtures cost $0; Ollama has no API fee.
Live inference uses configured rates and bounded calls. AWS resources created: none.
"""

import asyncio

from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.specialists import specialist
from common.trip_planning import TripRequest, catalog, validate_offer


def main() -> None:
    _, cfg = lesson_settings()
    request = TripRequest()
    records = []
    answer = asyncio.run(specialist(cfg, "flight", request, records))
    print("Context fields:", sorted(records[0]["context"]))
    print("Validated answer:", answer)
    # KEY IDEA: a schema alone cannot establish that a price is true.
    try:
        validate_offer({**answer, "cents": 1}, catalog("flight", request))
    except ValueError as exc:
        print("Rejected altered quote:", str(exc))
    complete()


if __name__ == "__main__":
    run_cli(main)
