"""Sequential and concurrent execution; race and resource limits.

Run: uv run python modules/05_building_tools/examples/07_tool_executors.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

import asyncio
import time

from strands import Agent, tool
from strands.tools.executors import ConcurrentToolExecutor, SequentialToolExecutor

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli
from common.testing import tool_message


@tool
async def inventory_check(section: str) -> str:
    """Read one synthetic inventory section without mutating shared state.

    Args:
        section: Either flights or hotels.
    """
    await asyncio.sleep(0.02)
    return section + " available"


def main() -> None:
    _, cfg = lesson_settings()
    calls = {
        "role": "assistant",
        "content": [
            tool_message("inventory_check", {"section": name}, name)["content"][0]
            for name in ("flights", "hotels")
        ],
    }
    for executor in (SequentialToolExecutor(), ConcurrentToolExecutor()):
        agent = Agent(
            model=get_model(cfg, responses=[calls, "Both inventories checked."]),
            tools=[inventory_check],
            tool_executor=executor,
            callback_handler=None,
            retry_strategy=None,
        )
        start = time.perf_counter()
        # KEY IDEA: independent reads can overlap; shared mutations need coordination.
        result = agent("Check flights and hotels together.", limits={"turns": 3})
        console.print(type(executor).__name__, "elapsed:", round(time.perf_counter() - start, 3))
        complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
