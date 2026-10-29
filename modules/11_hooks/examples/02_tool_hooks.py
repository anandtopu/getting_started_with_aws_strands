"""Tool hooks: Nimbus Tier 3 lesson.

Run: uv run python modules/11_hooks/examples/02_tool_hooks.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

from strands import Agent

from common.audit import AuditPolicy, quote_tool
from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import run_cli
from common.testing import tool_message


def main():
    _, cfg = lesson_settings()
    audit = AuditPolicy()
    agent = Agent(
        model=get_model(
            cfg,
            responses=[
                tool_message("quote_trip", {"destination": " bos "}),
                "Quote checked against the budget.",
            ],
        ),
        tools=[quote_tool()],
        hooks=[audit],
        callback_handler=None,
        retry_strategy=None,
    )
    # KEY IDEA: invocation state comes from the application, not model-generated tool arguments.
    result = agent(
        "Quote bos for traveler@example.com",
        invocation_state=dict(budget_cents=50000),
        limits={"turns": 3},
    )
    print("Normalized input:", agent.messages[1])
    print("Tool outcomes:", audit.rows)
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
