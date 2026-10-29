"""calculator, current_time, http_request and Open-Meteo; recorded offline weather.

Run: uv run python modules/06_community_tools/examples/01_calculator_time_weather.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No; live weather needs internet. Resources created: none.
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
        http_tool = weather_tool(client)
        model = get_model(
            cfg,
            responses=[
                tool_message("http_request", {"method": "GET", "url": WEATHER_URL}),
                tool_message("convert_budget", {"amount_usd": "100"}, "money"),
                "Lisbon fixture: 18.5 C; EUR 92 at an assumed rate, not a live quote.",
            ],
        )
        agent = Agent(
            model=model,
            tools=[http_tool, convert_budget],
            callback_handler=None,
            system_prompt="Nimbus travel day. Current time: " + travel_clock(args.mock),
            retry_strategy=None,
        )
        # KEY IDEA: operator-controlled HTTP transport enforces the one allowed endpoint.
        return await agent.invoke_async(
            "Fetch " + WEATHER_URL + " and convert USD 100 to EUR "
            "at the assumed rate 0.92. Distinguish fixture weather from live weather.",
            limits={"turns": 4},
        )


def main() -> None:
    args, cfg = lesson_settings()
    console.print("Weather source:", "synthetic recorded shape" if args.mock else "Open-Meteo live")
    complete(asyncio.run(run(args, cfg)), cfg)


if __name__ == "__main__":
    run_cli(main)
