"""AgentResult message, stop_reason, metrics, and agent.messages.

Run: uv run python modules/01_first_agent/examples/02_result_and_messages.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

from strands import Agent

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli


def main() -> None:
    _, cfg = lesson_settings()
    agent = Agent(
        model=get_model(cfg, responses=["Tell me your destination."]),
        callback_handler=None,
        retry_strategy=None,
    )
    result = agent(
        "Help me plan a Nimbus trip. Ask for my destination in one short sentence.",
        limits={"turns": 2},
    )
    # KEY IDEA: an AgentResult is more than the printable answer.
    console.print("stop_reason:", result.stop_reason)
    console.print("answer blocks:", result.message["content"])
    console.print("history roles:", [m["role"] for m in agent.messages])
    assert agent.messages[-1]["role"] == "assistant"
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
