"""Pydantic primer; structured_output_model on Agent/call and result.structured_output.

Run: uv run python modules/04_structured_output/examples/01_typed_ticket.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

from strands import Agent

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli
from common.schemas import TicketTriage
from common.testing import tool_message


def main() -> None:
    _, cfg = lesson_settings()
    prediction = {"category": "change", "urgency": "normal", "summary": "Change a standard fare."}
    model = get_model(cfg, responses=[tool_message("TicketTriage", prediction)])
    # KEY IDEA: the model produces a validated object, not JSON we trust without checking.
    agent = Agent(
        model=model,
        structured_output_model=TicketTriage,
        callback_handler=None,
        retry_strategy=None,
    )
    result = agent("Classify: Can I change my standard flight?", limits={"turns": 3})
    console.print(result.structured_output.model_dump(mode="json"))
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
