"""Limits: Nimbus Tier 3 lesson.

Run: uv run python modules/13_guardrails/examples/04_limits.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

from strands import Agent, tool

from common.audit import AuditPolicy
from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import run_cli
from common.testing import tool_message


def main():
    _, cfg = lesson_settings()

    @tool
    def ping() -> str:
        """Return a local fixed response."""
        return "pong"

    policy = AuditPolicy(allowed=("ping",), max_tools=1)
    agent = Agent(
        model=get_model(
            cfg, responses=[tool_message("ping", {}, "one"), tool_message("ping", {}, "two")]
        ),
        tools=[ping],
        hooks=[policy],
        callback_handler=None,
        retry_strategy=None,
    )
    result = agent("Check twice", limits={"turns": 2, "output_tokens": 200, "total_tokens": 1000})
    print("Stop reason:", result.stop_reason, "attempts:", policy.calls)
    print("Token limits apply at turn boundaries; use asyncio.timeout for a wall-clock bound.")
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
