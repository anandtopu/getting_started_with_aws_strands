"""Observe actual callback and multi-turn behavior through the SDK."""

from strands import Agent

from common.models import get_model


def test_callbacks_history_and_per_invocation_usage():
    deltas = []
    model = get_model(provider="mock", responses=["Lisbon noted.", "Budget noted."])
    agent = Agent(
        model=model, callback_handler=lambda **event: deltas.append(event.get("data", ""))
    )
    first = agent("Lisbon")
    second = agent("USD 600")
    assert "Lisbon noted." in "".join(deltas)
    assert len(agent.messages) == 4
    assert model.requests[1]["messages"][0]["content"][0]["text"] == "Lisbon"
    assert first.stop_reason == second.stop_reason == "end_turn"
