"""Tool filtering: Nimbus Tier 3 lesson.

Run: uv run python modules/14_mcp/examples/05_tool_filtering.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from strands import Agent

from common.lessons import complete, lesson_settings
from common.mcp_clients import reviewed_tools, stdio_booking
from common.models import get_model
from common.pretty import run_cli
from common.testing import tool_message


def main():
    _, cfg = lesson_settings()
    with TemporaryDirectory() as directory:
        with stdio_booking(Path(directory) / "mcp.db", allowed=["search_flights"]) as client:
            tools = reviewed_tools(client, ["nimbus_search_flights"])
            with stdio_booking(
                Path(directory) / "other.db", prefix="other", allowed=["get_booking"]
            ) as other:
                additional = reviewed_tools(other, ["other_get_booking"])
                print("Separate namespace:", [t.tool_name for t in additional])
                agent = Agent(
                    model=get_model(
                        cfg,
                        responses=[
                            tool_message("nimbus_search_flights", {"destination": "Porto"}),
                            "Synthetic Porto flights found.",
                        ],
                    ),
                    tools=[*tools, *additional],
                    callback_handler=None,
                    retry_strategy=None,
                )
                result = agent("Find flights to Porto", limits={"turns": 3})
                print("Reviewed tools:", [t.tool_name for t in tools])
                complete(result, cfg)
        # Client and server are closed before the database directory is removed.


if __name__ == "__main__":
    run_cli(main)
