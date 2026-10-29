"""Distinguish private application state from messages sent to a model.

Run: uv run python modules/09_memory/examples/01_state_and_messages.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

from strands import Agent

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli


def main() -> None:
    args, cfg = lesson_settings()
    agent = Agent(
        model=get_model(cfg, responses=["Please tell me your seat preference."]),
        callback_handler=None,
    )
    # KEY IDEA: state is not automatically a prompt; explicitly select any facts to expose.
    agent.state.set("seat", "aisle")
    result = agent(
        "Can you see a preference that the application has not sent?", limits={"turns": 2}
    )
    console.print("Private state:", agent.state.get("seat"))
    console.print("Message roles:", [m["role"] for m in agent.messages])
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
