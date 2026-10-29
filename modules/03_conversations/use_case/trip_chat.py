"""Keep a short trip conversation and show the retained history.

Run: uv run python modules/03_conversations/use_case/trip_chat.py --mock
Expected: a Nimbus result followed by Lesson complete.
Cost: mock/local $0 hosted inference; hosted mode uses model tokens.
AWS resources created: none. Concepts: compose this module's taught APIs.
"""

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli


def main() -> None:
    _, cfg = lesson_settings()
    manager = SlidingWindowConversationManager(window_size=4)
    agent = Agent(
        model=get_model(
            cfg,
            responses=[
                "Lisbon noted.",
                "Budget $600 noted.",
                "Two travelers, Lisbon, budget $600; please confirm dates.",
            ],
        ),
        conversation_manager=manager,
        callback_handler=None,
        retry_strategy=None,
        system_prompt="Nimbus planner: ask for dates and budget, never invent availability.",
    )
    # KEY IDEA: a message window is a memory budget, not durable storage of traveler preferences.
    for prompt in [
        "I want Lisbon.",
        "My budget is $600.",
        "Two travelers. Summarize and ask a question.",
    ]:
        result = agent(prompt, limits={"turns": 2})
        console.print("Retained messages:", len(agent.messages))
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
