"""TOOL_SPEC modules and direct agent.tool calls.

Run: uv run python modules/05_building_tools/examples/06_module_tools.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

from strands import Agent

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli
from common.tools import policy_lookup


def main() -> None:
    _, cfg = lesson_settings()
    agent = Agent(
        model=get_model(cfg, responses=[] if cfg.provider == "mock" else None),
        tools=[policy_lookup],
        callback_handler=None,
    )
    # KEY IDEA: direct calls use registered tool schemas but do not ask the model to choose.
    result = agent.tool.policy_lookup()
    assert result["status"] == "success"
    console.print(result)
    console.print("Direct calls recorded in history:", len(agent.messages))
    complete()


if __name__ == "__main__":
    run_cli(main)
