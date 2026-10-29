"""Prepare a Lisbon travel-day brief with constrained HTTP and a currency tool.

Run: uv run python modules/06_community_tools/use_case/travel_day_helper.py --mock
Expected: a Nimbus result followed by Lesson complete.
Cost: mock/local $0 hosted inference; hosted mode uses model tokens.
AWS resources created: none. Concepts: compose this module's taught APIs.
"""

import asyncio

from strands import Agent

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli
from common.testing import tool_message
from common.tools.travel_day import (
    WEATHER_URL,
    convert_budget,
    travel_clock,
    weather_client,
    weather_tool,
)


async def run(args, cfg):
    async with weather_client(args.mock) as client:
        model = get_model(
            cfg,
            responses=[
                tool_message("http_request", {"method": "GET", "url": WEATHER_URL}),
                tool_message("convert_budget", {"amount_usd": "150"}, "convert"),
                "Lisbon weather fixture: 18.5 C, no precipitation. EUR 138 at the assumed rate.",
            ],
        )
        agent = Agent(
            model=model,
            tools=[weather_tool(client), convert_budget],
            system_prompt="Nimbus travel day; timestamp " + travel_clock(args.mock),
            callback_handler=None,
            retry_strategy=None,
        )
        # KEY IDEA: API requests and money calculations are explicit, separately checked tools.
        return await agent.invoke_async(
            "Use " + WEATHER_URL + " and convert USD 150 at 0.92 EUR/USD. "
            "Say that the exchange rate is assumed. Give a short departure-day brief.",
            limits={"turns": 4},
        )


def main() -> None:
    args, cfg = lesson_settings()
    console.print("Weather mode:", "synthetic fixture" if args.mock else "live Open-Meteo")
    complete(asyncio.run(run(args, cfg)), cfg)


if __name__ == "__main__":
    run_cli(main)
