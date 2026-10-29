"""@tool(context=True), ToolContext, private agent state and invocation state.

Run: uv run python modules/05_building_tools/examples/03_tool_context.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

from strands import Agent, ToolContext, tool

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import run_cli
from common.testing import tool_message


@tool(context=True)
def traveler_preferences(tool_context: ToolContext) -> dict:
    """Read trusted identity and private seat preference for this invocation."""
    return {
        "customer": tool_context.invocation_state["customer_id"],
        "seat": tool_context.agent.state.get("seat"),
    }


def main() -> None:
    _, cfg = lesson_settings()
    model = get_model(
        cfg,
        responses=[
            tool_message("traveler_preferences", {}),
            "Traveler CUS-001 prefers an aisle seat.",
        ],
    )
    agent = Agent(
        model=model,
        tools=[traveler_preferences],
        state={"seat": "aisle"},
        callback_handler=None,
        retry_strategy=None,
    )
    # KEY IDEA: context is injected by the application, not chosen as a model argument.
    assert "tool_context" not in traveler_preferences.tool_spec["inputSchema"]["json"]["properties"]
    result = agent(
        "Read my saved seat preference.",
        invocation_state={"customer_id": "CUS-001"},
        limits={"turns": 3},
    )
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
