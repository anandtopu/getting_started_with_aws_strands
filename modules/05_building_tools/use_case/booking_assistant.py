"""Search flights/hotels, check seats, and inspect an authorized booking.

Run: uv run python modules/05_building_tools/use_case/booking_assistant.py --mock
Expected: a Nimbus result followed by Lesson complete.
Cost: mock/local $0 hosted inference; hosted mode uses model tokens.
AWS resources created: none. Concepts: compose this module's taught APIs.
"""

from common.assistant import booking_agent
from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.testing import tool_message
from common.tools.booking import search_flights


def main() -> None:
    _, cfg = lesson_settings()
    first = search_flights("Lisbon")[0]
    replies = [
        tool_message("search_flights", {"destination": "Lisbon"}),
        tool_message("search_hotels", {"city": "Lisbon"}, "hotels"),
        tool_message("check_seat_availability", {"flight_id": first["flight_id"]}, "seats"),
        tool_message("get_booking", {"booking_id": "BKG-0001"}, "booking"),
        "Synthetic options found; booking BKG-0001 is confirmed. No reservation was made.",
    ]
    agent = booking_agent(cfg, replies)
    # KEY IDEA: the authenticated application supplies identity, outside model arguments.
    result = agent(
        "Search Lisbon flights and hotels, check one flight's seats, then my BKG-0001 booking. "
        "Summarize one flight, one hotel and the booking status in at most 100 words.",
        invocation_state={"customer_id": "CUS-001"},
        limits={"turns": 6},
    )
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
