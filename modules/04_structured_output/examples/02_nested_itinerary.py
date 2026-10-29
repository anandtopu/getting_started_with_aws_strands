"""Nested schemas, enums and optional fields; extract a confirmation email.

Run: uv run python modules/04_structured_output/examples/02_nested_itinerary.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

from strands import Agent

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli
from common.schemas import Itinerary
from common.testing import tool_message


def main() -> None:
    _, cfg = lesson_settings()
    payload = {
        "traveler": "Demo Traveler",
        "legs": [{"flight_id": "FLT-0001", "destination": "Lisbon", "price_cents": 25000}],
        "total_cents": 25000,
    }
    agent = Agent(
        model=get_model(cfg, responses=[tool_message("Itinerary", payload)]),
        callback_handler=None,
        retry_strategy=None,
    )
    # KEY IDEA: nested validation checks both field types and relationships between fields.
    result = agent(
        "Extract: Demo Traveler flies FLT-0001 to Lisbon for USD 250. "
        "Flight total USD 250; no hotel booked.",
        structured_output_model=Itinerary,
        limits={"turns": 3},
    )
    console.print(result.structured_output.model_dump(mode="json"))
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
