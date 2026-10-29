"""Bound repairs and prevent treating typed-but-invented output as trustworthy."""

import pytest
from strands import Agent

from common.models import get_model
from common.schemas import Itinerary, TicketTriage, validate_inventory
from common.testing import tool_message


def test_nested_mismatch_and_invented_flight_rejected():
    payload = {
        "traveler": "Demo Traveler",
        "legs": [{"flight_id": "FLT-9999", "destination": "Lisbon", "price_cents": 100}],
        "total_cents": 100,
    }
    with pytest.raises(ValueError, match="inventory"):
        validate_inventory(Itinerary.model_validate(payload))
    with pytest.raises(ValueError, match="sum of flight prices"):
        Itinerary.model_validate({**payload, "total_cents": 101})


def test_repair_budget_stops_invalid_predictions():
    model = get_model(
        provider="mock",
        responses=[
            tool_message(
                "TicketTriage",
                {"category": "invalid", "urgency": "normal", "summary": "A support request."},
            )
        ]
        * 3,
    )
    agent = Agent(
        model=model,
        structured_output_model=TicketTriage,
        callback_handler=None,
        retry_strategy=None,
    )
    result = agent("Classify a refund", limits={"turns": 2})
    assert result.stop_reason == "limit_turns" and result.structured_output is None
    assert model.index == 2
