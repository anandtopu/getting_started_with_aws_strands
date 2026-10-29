"""Concurrency and cancel: Nimbus Tier 3 lesson.

Run: uv run python modules/10_streaming/examples/02_concurrency_and_cancel.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

import asyncio

from strands import Agent, tool

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import run_cli
from common.streaming import planner
from common.testing import tool_message


async def demo(cfg):
    gate = asyncio.Semaphore(2)

    async def plan(city):
        async with gate:
            return str(await planner(cfg).invoke_async("Plan " + city, limits={"turns": 2}))

    print(await asyncio.gather(*(plan(c) for c in ["Boston", "Porto", "Tokyo"])))
    stopped = asyncio.Event()

    @tool
    async def slow_lookup() -> str:
        """Wait locally to make cancellation observable; creates no external work."""
        try:
            await asyncio.sleep(30)
            return "finished"
        finally:
            stopped.set()

    agent = Agent(
        model=get_model(provider="mock", responses=[tool_message("slow_lookup", {})]),
        tools=[slow_lookup],
        callback_handler=None,
        retry_strategy=None,
    )
    # KEY IDEA: wait_for cancels cooperative async work; it cannot undo external side effects.
    try:
        await asyncio.wait_for(agent.invoke_async("Wait"), timeout=0.15)
    except TimeoutError:
        print("Timed out; async tool cleanup:", stopped.is_set())


def main():
    _, cfg = lesson_settings()
    asyncio.run(demo(cfg))
    complete()


if __name__ == "__main__":
    run_cli(main)
