"""Async/await primer and invoke_async.

Run: uv run python modules/01_first_agent/examples/04_async_call.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

import asyncio

from strands import Agent

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import run_cli


async def answer(cfg):
    agent = Agent(
        model=get_model(cfg, responses=["Nimbus async reply."]),
        callback_handler=None,
        retry_strategy=None,
    )
    # KEY IDEA: await lets other coroutines run while the model is waiting.
    return await agent.invoke_async("Give a short Nimbus welcome.", limits={"turns": 2})


def main() -> None:
    _, cfg = lesson_settings()
    complete(asyncio.run(answer(cfg)), cfg)


if __name__ == "__main__":
    run_cli(main)
