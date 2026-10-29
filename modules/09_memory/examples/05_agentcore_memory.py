"""Optional AgentCore adapter: scoped recall with persistence disabled in this lesson.

Run: uv run --group aws python modules/09_memory/examples/05_agentcore_memory.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

import asyncio
import json

from strands import Agent

from common.lessons import complete, lesson_settings
from common.memory_adapters import agentcore_manager
from common.models import get_model
from common.pretty import run_cli


def main() -> None:
    args, cfg = lesson_settings()
    with agentcore_manager(mock=args.mock) as manager:
        # KEY IDEA: a trusted actor and namespace constrain which memories are retrieved.
        memories = asyncio.run(manager.search("seat preference"))
        agent = Agent(
            model=get_model(cfg, responses=["Your recorded preference is an aisle seat."]),
            memory_manager=manager,
            callback_handler=None,
            retry_strategy=None,
            system_prompt="Answer only from the supplied memories. If empty, say you do not know.",
        )
        result = agent(
            json.dumps(
                {"question": "What seat do I prefer?", "memories": [m.content for m in memories]}
            ),
            limits={"turns": 2},
        )
        complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
