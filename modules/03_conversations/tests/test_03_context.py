"""Compare actual loss of history and a model-produced summary."""

import runpy

from strands import Agent
from strands.agent.conversation_manager import (
    SlidingWindowConversationManager,
    SummarizingConversationManager,
)

from common.config import ROOT
from common.models import get_model


def test_window_and_summary_have_distinct_behavior():
    source = runpy.run_path(
        str(ROOT / "modules/03_conversations/examples/02_conversation_windows.py")
    )
    agent = Agent(
        model=get_model(provider="mock", responses=["Lisbon; budget USD 600."]),
        messages=source["history"](),
        callback_handler=None,
    )
    SlidingWindowConversationManager(window_size=4).apply_management(agent)
    assert len(agent.messages) <= 4
    agent.messages = source["history"]()
    SummarizingConversationManager(preserve_recent_messages=2).reduce_context(agent)
    assert len(agent.messages) < 8
    assert any("budget USD 600" in str(message) for message in agent.messages)
