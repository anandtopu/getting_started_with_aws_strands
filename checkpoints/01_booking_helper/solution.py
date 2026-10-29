"""Search trips and return an inventory-checked, structured flight itinerary.

Run: uv run python checkpoints/01_booking_helper/solution.py --mock
Expected: a validated Itinerary with a real synthetic flight ID and price.
Concepts: tools, trusted identity, structured output and application validation.
Cost: mock/local $0 hosted inference; hosted calls use tokens. AWS resources: none.
"""

from decimal import Decimal

from common.assistant import booking_agent
from common.lessons import complete, lesson_settings
from common.pretty import console, run_cli
from common.schemas import validate_inventory
from common.testing import tool_message
from common.tools.booking import search_flights, search_hotels


def itinerary_script() -> list:
    flight, hotel = search_flights("Lisbon")[0], search_hotels("Lisbon")[0]
    price = int(Decimal(flight["price_usd"]) * 100)
    return [
        tool_message("search_flights", {"destination": "Lisbon"}),
        tool_message("search_hotels", {"city": "Lisbon"}, "hotels"),
        tool_message("get_booking", {"booking_id": "BKG-0001"}, "booking"),
        tool_message("check_seat_availability", {"flight_id": flight["flight_id"]}, "seats"),
        tool_message(
            "Itinerary",
            {
                "traveler": "Demo Traveler",
                "legs": [
                    {
                        "flight_id": flight["flight_id"],
                        "destination": "Lisbon",
                        "price_cents": price,
                    }
                ],
                "total_cents": price,
                "hotel_id": hotel["hotel_id"],
            },
            "answer",
        ),
    ]


def main() -> None:
    _, cfg = lesson_settings()
    agent = booking_agent(cfg, itinerary_script(), structured=True)
    result = agent(
        "Find Lisbon flights and hotels, check my BKG-0001 booking, and check "
        "one flight's seats. Return a flight itinerary with its actual synthetic price. "
        "Name the traveler Demo Traveler. Do not reserve anything.",
        invocation_state={"customer_id": "CUS-001"},
        limits={"turns": 7},
    )
    if result.structured_output is None:
        raise ValueError("No valid itinerary within the turn budget")
    # KEY IDEA: a well-typed answer can still invent facts; verify it against inventory.
    validate_inventory(result.structured_output)
    console.print(result.structured_output.model_dump(mode="json"))
    console.print("Prices are synthetic. No reservation was made. Total covers flights only.")
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
