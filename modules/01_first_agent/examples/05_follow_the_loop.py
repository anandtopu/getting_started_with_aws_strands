"""Agent/event loop; model decision, tool execution, continuation and stop.

Run: uv run python modules/01_first_agent/examples/05_follow_the_loop.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

from strands import Agent, tool

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli
from common.testing import tool_message


@tool
def refund_window() -> str:
    """Read the short synthetic cancellation condition."""
    console.print("2. Tool executed")
    return "24 hours after booking AND departure at least 7 days after creation."


def main() -> None:
    _, cfg = lesson_settings()
    model = get_model(
        cfg,
        responses=[
            tool_message("refund_window", {}),
            "Both the 24-hour and 7-day conditions apply.",
        ],
    )
    agent = Agent(model=model, tools=[refund_window], callback_handler=None, retry_strategy=None)
    console.print("1. Model receives request and may ask for a tool")
    # KEY IDEA: Strands feeds the toolResult back into another model turn.
    result = agent("Read and explain the refund window.", limits={"turns": 3})
    console.print(
        "3. Tool result in history:",
        any("toolResult" in block for msg in agent.messages for block in msg["content"]),
    )
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
