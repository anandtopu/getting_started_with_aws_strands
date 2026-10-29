"""Stream events: Nimbus Tier 3 lesson.

Run: uv run python modules/10_streaming/examples/01_stream_events.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

import asyncio

from strands import Agent, tool

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli
from common.testing import tool_message


async def demo(cfg):
    @tool
    def trip_stop() -> str:
        """Return a fixed synthetic stop."""
        return "Boston waterfront"

    callback_keys = []
    scripted = tool_message("trip_stop", {})
    scripted["content"].insert(
        0,
        {
            "reasoningContent": {
                "reasoningText": {"text": "Fixture planning summary: inspect the available stop."}
            }
        },
    )
    agent = Agent(
        model=get_model(cfg, responses=[scripted, "Visit the Boston waterfront."]),
        tools=[trip_stop],
        callback_handler=lambda **e: callback_keys.extend(e),
        retry_strategy=None,
    )
    # KEY IDEA: a stream includes lifecycle/tool events as well as displayable text.
    keys = set()
    async for event in agent.stream_async("Suggest a stop", limits={"turns": 3}):
        keys.update(event)
        if "data" in event:
            console.print(event["data"])
    console.print("Iterator event keys:", sorted(keys))
    console.print("Callback keys:", sorted(set(callback_keys)))
    console.print("Reasoning appears only if the provider exposes it; do not log private input.")


def main():
    _, cfg = lesson_settings()
    asyncio.run(demo(cfg))
    complete()


if __name__ == "__main__":
    run_cli(main)
