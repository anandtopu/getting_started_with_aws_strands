"""Supported tool replacements: constrained HTTP, Decimal money and injected time."""

from datetime import UTC, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import httpx
from strands import tool
from strands.vended_tools.http_request import make_http_request

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast?latitude=38.72&longitude=-9.14"
    "&current=temperature_2m,precipitation&timezone=UTC"
)
WEATHER_FIXTURE = {
    "latitude": 38.72,
    "longitude": -9.14,
    "current": {"time": "2027-04-01T12:00", "temperature_2m": 18.5, "precipitation": 0.0},
}


@tool
def convert_budget(amount_usd: str, usd_to_eur: str = "0.92") -> str:
    """Convert a budget using an explicitly supplied teaching exchange rate.

    Args:
        amount_usd: Positive USD amount as a decimal string, at most 100000.
        usd_to_eur: Assumed EUR per USD, greater than zero and at most 10; not live FX.
    """
    amount, rate = Decimal(amount_usd), Decimal(usd_to_eur)
    if (
        not amount.is_finite()
        or not rate.is_finite()
        or not 0 < amount <= 100000
        or not 0 < rate <= 10
    ):
        raise ValueError("Supply finite positive amounts and a bounded teaching rate")
    return f"EUR {(amount * rate).quantize(Decimal('0.01'))}; assumed rate, not a live quote"


def travel_clock(mock: bool, timezone: str = "Europe/Lisbon") -> str:
    instant = datetime(2027, 4, 1, 12, tzinfo=UTC) if mock else datetime.now(UTC)
    return instant.astimezone(ZoneInfo(timezone)).isoformat()


def weather_client(mock: bool) -> httpx.AsyncClient:
    async def allow_forecast(request: httpx.Request) -> None:
        if request.method != "GET" or str(request.url) != WEATHER_URL:
            raise PermissionError("Only the fixed Lisbon forecast GET is allowed")

    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=WEATHER_FIXTURE))
    return httpx.AsyncClient(
        transport=transport if mock else None,
        follow_redirects=False,
        timeout=10,
        event_hooks={"request": [allow_forecast]},
    )


def weather_tool(client: httpx.AsyncClient):
    return make_http_request(
        client=client, description="GET only the approved Lisbon forecast URL."
    )
