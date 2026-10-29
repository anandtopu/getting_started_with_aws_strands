"""retrieve, memory, think, use_llm, image_reader, journal, handoff_to_user; mix with custom tools.

Run: uv run python modules/06_community_tools/examples/04_tool_catalog.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: Optional; AWS tool adapters use fixtures locally. Resources created: none.
"""

from contextlib import nullcontext
from unittest.mock import patch

from strands import Agent
from strands.vended_tools.notebook import notebook
from strands_tools import handoff_to_user, image_reader, use_agent

from common.data import data_path
from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli


def main() -> None:
    args, cfg = lesson_settings()
    console.print("Deprecated names and supported replacements: see MIGRATIONS.md in this module.")
    agent = Agent(
        model=get_model(cfg, responses=["Ask the traveler for dates before recommending."]),
        tools=[notebook, use_agent, image_reader, handoff_to_user],
        callback_handler=None,
        retry_strategy=None,
    )
    # KEY IDEA: session notes are private state until a tool returns their content.
    console.print(agent.tool.notebook(mode="create", name="trip", new_str="Lisbon; budget 600"))
    console.print(agent.tool.notebook(mode="read", name="trip"))
    console.print(
        agent.tool.image_reader(image_path=str(data_path("receipts/receipt_01.png")))["status"]
    )
    console.print(
        agent.tool.use_agent(
            prompt="What trip detail should we ask for next?",
            system_prompt="You are a concise Nimbus specialist.",
            tools=[],
        )
    )
    context = (
        patch.object(handoff_to_user, "get_user_input", return_value="Two travelers")
        if args.mock
        else nullcontext()
    )
    with context:
        console.print(agent.tool.handoff_to_user(message="How many travelers?"))
    complete()


if __name__ == "__main__":
    run_cli(main)
