"""Bounded read-only tools; customer identity comes from trusted invocation state."""

from decimal import Decimal

from strands import ToolContext, tool

from common.data import bookings_connection, load_csv


@tool
def search_flights(destination: str, max_price_usd: int = 700) -> list[dict]:
    """Find up to five available Nimbus flights.

    Args:
        destination: Exact destination city, compared without case sensitivity.
        max_price_usd: Maximum fare in whole USD, from 1 to 2000.
    """
    if not 1 <= max_price_usd <= 2000:
        raise ValueError("max_price_usd must be between 1 and 2000")
    return [
        r
        for r in load_csv("flights.csv")
        if r["destination"].casefold() == destination.casefold()
        and Decimal(r["price_usd"]) <= max_price_usd
        and int(r["seats_left"]) > 0
    ][:5]


@tool
def search_hotels(city: str, max_nightly_usd: int = 300) -> list[dict]:
    """Find up to five synthetic hotels within a nightly budget.

    Args:
        city: Exact destination city.
        max_nightly_usd: Nightly maximum in whole USD, from 1 to 2000.
    """
    if not 1 <= max_nightly_usd <= 2000:
        raise ValueError("max_nightly_usd must be between 1 and 2000")
    return [
        r
        for r in load_csv("hotels.csv")
        if r["city"].casefold() == city.casefold()
        and Decimal(r["nightly_price_usd"]) <= max_nightly_usd
    ][:5]


@tool(context=True)
def get_booking(booking_id: str, tool_context: ToolContext) -> dict:
    """Look up one booking belonging to the authenticated traveler.

    Args:
        booking_id: Nimbus booking reference, for example BKG-0001.
        tool_context: Injected context; the model cannot choose the customer ID.
    """
    customer_id = tool_context.invocation_state.get("customer_id")
    if not customer_id:
        raise PermissionError("A trusted customer identity is required")
    with bookings_connection() as db:
        row = db.execute(
            "SELECT booking_id,status,total_cents FROM bookings "
            "WHERE booking_id=? AND customer_id=?",
            (booking_id, customer_id),
        ).fetchone()
    if row is None:
        raise ValueError("Booking unavailable for this traveler")
    return dict(row)


@tool
def check_seat_availability(flight_id: str, travelers: int = 1) -> dict:
    """Check inventory without reserving a seat.

    Args:
        flight_id: Flight reference such as FLT-0001.
        travelers: Requested seats, from 1 to 9.
    """
    if not 1 <= travelers <= 9:
        raise ValueError("travelers must be between 1 and 9")
    for row in load_csv("flights.csv"):
        if row["flight_id"] == flight_id:
            return {
                "flight_id": flight_id,
                "available": int(row["seats_left"]) >= travelers,
                "seats_left": int(row["seats_left"]),
            }
    raise ValueError("Unknown flight ID")
