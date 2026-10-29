"""Tool interrupt: Nimbus Tier 3 lesson.

Run: uv run python modules/12_interrupts/examples/02_tool_interrupt.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

from strands import Agent, tool
from strands.types.tools import ToolContext

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import run_cli
from common.testing import tool_message


def main():
    _, cfg = lesson_settings()

    @tool(context=True)
    def choose_contact(tool_context: ToolContext) -> str:
        """Ask a human for a preferred contact channel; does not authorize money movement."""
        answer = tool_context.interrupt("contact-choice", reason="Choose email or phone")
        return answer if answer in {"email", "phone"} else "No valid choice"

    agent = Agent(
        model=get_model(cfg, responses=[tool_message("choose_contact", {}), "Choice recorded."]),
        tools=[choose_contact],
        callback_handler=None,
        retry_strategy=None,
    )
    result = agent("Ask for a contact preference", limits={"turns": 3})
    if result.stop_reason == "interrupt":
        result = agent(
            [{"interruptResponse": {"interruptId": result.interrupts[0].id, "response": "email"}}]
        )
    # Simpler console handoff is supported, but it is not a durable approval system.
    from unittest.mock import patch

    from strands_tools import handoff_to_user

    with patch("strands_tools.handoff_to_user.get_user_input", return_value="email"):
        simple = Agent(
            model=get_model(cfg, responses=[]), tools=[handoff_to_user], callback_handler=None
        )
        print(
            simple.tool.handoff_to_user(message="Choose a contact channel", breakout_of_loop=False)
        )
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
