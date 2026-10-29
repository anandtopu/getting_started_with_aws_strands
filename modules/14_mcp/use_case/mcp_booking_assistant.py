"""booking assistant: Nimbus Tier 3 lesson.

Run: uv run python modules/14_mcp/use_case/mcp_booking_assistant.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from strands import Agent

from common.lessons import complete, lesson_settings
from common.mcp_clients import reviewed_tools, stdio_booking
from common.models import get_model
from common.pretty import run_cli
from common.pricing_agent import lambda_cost_question
from common.testing import tool_message


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pricing-live", action="store_true")
    args, cfg = lesson_settings(parser)
    with TemporaryDirectory() as directory:
        with stdio_booking(Path(directory) / "bookings.db") as client:
            tools = reviewed_tools(
                client, ["nimbus_search_flights", "nimbus_create_booking", "nimbus_get_booking"]
            )
            agent = Agent(
                model=get_model(
                    cfg,
                    responses=[
                        tool_message("nimbus_search_flights", {"destination": "Porto"}, "search"),
                        tool_message(
                            "nimbus_create_booking",
                            {"flight_id": "FLT-0001", "idempotency_key": "trip-demo"},
                            "reserve",
                        ),
                        "A local synthetic reservation was created; no airline purchase occurred.",
                    ],
                ),
                tools=tools,
                callback_handler=None,
                retry_strategy=None,
                system_prompt=(
                    "Search then book one synthetic flight. Use idempotency key trip-demo."
                ),
            )
            complete(agent("Find and reserve a Porto flight", limits={"turns": 4}), cfg)
    if args.pricing_live and not args.mock:
        from common.aws_mcp import aws_server

        with aws_server(cfg, "pricing") as client:
            complete(lambda_cost_question(cfg, client=client), cfg)
    else:
        print("Pricing question uses illustrative evidence; no AWS server launched.")
        complete(lambda_cost_question(cfg), cfg)


if __name__ == "__main__":
    run_cli(main)
