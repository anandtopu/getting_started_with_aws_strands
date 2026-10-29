"""SlidingWindowConversationManager, SummarizingConversationManager, NullConversationManager and
overflow.

Run: uv run python modules/03_conversations/examples/02_conversation_windows.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

from strands import Agent
from strands.agent.conversation_manager import (
    NullConversationManager,
    SlidingWindowConversationManager,
    SummarizingConversationManager,
)
from strands.types.exceptions import ContextWindowOverflowException

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli


def history() -> list[dict]:
    return [
        {"role": role, "content": [{"text": text}]}
        for _ in range(4)
        for role, text in [("user", "Lisbon; budget $600"), ("assistant", "Noted.")]
    ]


def main() -> None:
    _, cfg = lesson_settings()
    sliding = SlidingWindowConversationManager(window_size=4)
    summarizing = SummarizingConversationManager(preserve_recent_messages=2)
    # KEY IDEA: trimming discards detail; summarizing calls a model and may lose detail too.
    for manager in (sliding, summarizing, NullConversationManager()):
        model = get_model(cfg, responses=["Traveler chose Lisbon with budget $600."])
        agent = Agent(
            model=model,
            messages=history(),
            conversation_manager=manager,
            callback_handler=None,
            retry_strategy=None,
        )
        if isinstance(manager, SlidingWindowConversationManager):
            manager.apply_management(agent)
        elif isinstance(manager, SummarizingConversationManager):
            manager.reduce_context(agent)
        else:
            try:
                manager.reduce_context(agent, ContextWindowOverflowException("Context too large"))
            except ContextWindowOverflowException as exc:
                console.print("Expected overflow:", str(exc))
        console.print(type(manager).__name__, "messages remaining:", len(agent.messages))
    complete()


if __name__ == "__main__":
    run_cli(main)
