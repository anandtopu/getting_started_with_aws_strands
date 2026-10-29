"""Named Nimbus versions composed from capabilities already taught."""

from strands import Agent

from common.config import Settings
from common.data import data_path
from common.models import get_model
from common.schemas import Itinerary
from common.tools.booking import (
    check_seat_availability,
    get_booking,
    search_flights,
    search_hotels,
)


def faq_agent(settings: Settings, responses=None) -> Agent:
    return Agent(
        model=get_model(settings, responses=responses),
        callback_handler=None,
        retry_strategy=None,
        system_prompt="You are Nimbus's concise FAQ assistant. Use only this policy; "
        "say you do not know when it does not answer.\n"
        + data_path("policies/refund.md").read_text(encoding="utf-8"),
    )


def booking_agent(settings: Settings, responses=None, *, structured: bool = False) -> Agent:
    return Agent(
        model=get_model(settings, responses=responses),
        callback_handler=None,
        retry_strategy=None,
        system_prompt="You are Nimbus's booking helper. Search before recommending. "
        "Use only returned inventory. Check availability. Prices are synthetic. "
        "Do not reserve or change bookings. Itinerary totals include flights only.",
        tools=[search_flights, search_hotels, get_booking, check_seat_availability],
        structured_output_model=Itinerary if structured else None,
    )
