"""Inspect the Trip Planning Crew inputs before wiring the graph.

Run: uv run python checkpoints/04_trip_planning_crew/starter.py --mock
Expected: catalog subtotal 52800 cents. Cost $0; AWS resources: none.
"""

from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.trip_planning import TripRequest, catalog


def main() -> None:
    lesson_settings()
    request = TripRequest()
    quotes = [catalog(role, request) for role in ("flight", "hotel")]
    print("Request:", request.model_dump())
    print("Catalog subtotal:", sum(q["cents"] for q in quotes))
    print("Next: implement parse, parallel specialists, budget, review and draft routing.")
    complete()


if __name__ == "__main__":
    run_cli(main)
