"""Async tools, streamed tool progress and consumption.

Run: uv run python modules/05_building_tools/examples/04_async_progress.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

import asyncio

from strands import Agent, tool

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli
from common.testing import tool_message


@tool
async def check_trip():
    """Stream progress while checking synthetic trip availability."""
    yield {"progress": "checking flights"}
    await asyncio.sleep(0)
    yield {"progress": "checking hotels"}
    # The final yielded item becomes the tool's returned value.
    yield {"status": "success", "content": [{"text": "Synthetic inventory checked."}]}


async def run(cfg):
    agent = Agent(
        model=get_model(cfg, responses=[tool_message("check_trip", {}), "Trip checks finished."]),
        tools=[check_trip],
        callback_handler=None,
        retry_strategy=None,
    )
    result = None
    async for event in agent.stream_async("Check my trip.", limits={"turns": 3}):
        # KEY IDEA: progress arrives before the final agent answer.
        if "tool_stream_event" in event:
            console.print("Progress:", event["tool_stream_event"]["data"])
        result = event.get("result", result)
    return result


def main() -> None:
    _, cfg = lesson_settings()
    complete(asyncio.run(run(cfg)), cfg)


if __name__ == "__main__":
    run_cli(main)
