"""Run the full checkpoint through actual tools and validate its output."""

import runpy

from common.assistant import booking_agent
from common.config import ROOT, Settings
from common.schemas import validate_inventory


def test_reference_solution_trajectory_and_inventory():
    source = runpy.run_path(str(ROOT / "checkpoints/01_booking_helper/solution.py"))
    agent = booking_agent(Settings(provider="mock"), source["itinerary_script"](), structured=True)
    result = agent(
        "Find Lisbon options and my booking.",
        invocation_state={"customer_id": "CUS-001"},
        limits={"turns": 7},
    )
    validate_inventory(result.structured_output)
    calls = [
        block["toolUse"]["name"]
        for message in agent.messages
        for block in message["content"]
        if "toolUse" in block
    ]
    assert calls == [
        "search_flights",
        "search_hotels",
        "get_booking",
        "check_seat_availability",
        "Itinerary",
    ]
