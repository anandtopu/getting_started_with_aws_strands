"""Text content blocks, agent.messages, multi-turn state and role/constraints/tone/output prompts.

Run: uv run python modules/03_conversations/examples/01_multi_turn.py --mock
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
        model=get_model(
            cfg, responses=["I noted Lisbon and a $600 budget.", "Your destination is Lisbon."]
        ),
        system_prompt="Role: Nimbus planner. Constraints: invent no availability. "
        "Tone: concise. Format: destination, budget, next question.",
        callback_handler=None,
        retry_strategy=None,
    )
    agent("Plan Lisbon with a $600 budget.", limits={"turns": 2})
    # KEY IDEA: text content blocks and earlier messages travel with the next request.
    result = agent([{"text": "Which destination did I choose?"}], limits={"turns": 2})
    console.print("Message roles:", [m["role"] for m in agent.messages])
    assert len(agent.messages) == 4
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
