"""Local guardrails: Nimbus Tier 3 lesson.

Run: uv run python modules/13_guardrails/examples/01_local_guardrails.py --mock
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
    policy = AuditPolicy(max_tools=1)
    agent = Agent(
        model=get_model(
            cfg,
            responses=[
                tool_message("quote_trip", {"destination": "LAX"}),
                "The trip exceeds this budget.",
            ],
        ),
        tools=[quote_tool()],
        hooks=[policy],
        callback_handler=None,
        retry_strategy=None,
    )
    result = agent(
        "Quote Los Angeles", invocation_state=dict(budget_cents=50000), limits={"turns": 3}
    )
    print("Denied attempts:", [r for r in policy.rows if r.get("blocked")])
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
