"""toolUse, toolResult, status and tool exception feedback.

Run: uv run python modules/05_building_tools/examples/02_results_and_errors.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

from strands import Agent, tool

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli
from common.testing import tool_message


@tool
def validate_reference(reference: str) -> dict:
    """Validate the Nimbus booking prefix before lookup.

    Args:
        reference: Booking reference supplied by the traveler.
    """
    if not reference.startswith("BKG-"):
        return {"status": "error", "content": [{"text": "Reference must start BKG-"}]}
    raise ValueError("Booking service unavailable in this failure demo")


def main() -> None:
    _, cfg = lesson_settings()
    model = get_model(
        cfg,
        responses=[
            tool_message("validate_reference", {"reference": "bad"}),
            tool_message("validate_reference", {"reference": "BKG-0001"}, "retry"),
            "Please retry later; no booking was changed.",
        ],
    )
    agent = Agent(
        model=model, tools=[validate_reference], callback_handler=None, retry_strategy=None
    )
    result = agent("Validate bad, then BKG-0001; explain any failure.", limits={"turns": 4})
    # KEY IDEA: both explicit errors and exceptions become toolResult feedback.
    statuses = [
        b["toolResult"]["status"] for m in agent.messages for b in m["content"] if "toolResult" in b
    ]
    console.print("Tool statuses:", statuses)
    if cfg.provider == "mock":
        assert statuses == ["error", "error"]
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
