"""Validation failure, correction, retry limits and malformed output tests.

Run: uv run python modules/04_structured_output/examples/03_validation_retry.py --mock
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
    bad = {"category": "made-up", "urgency": "normal", "summary": "A refund request."}
    fixed = {**bad, "category": "refund"}
    model = get_model(
        cfg,
        responses=[
            tool_message("TicketTriage", bad, "bad"),
            tool_message("TicketTriage", fixed, "fixed"),
        ],
    )
    agent = Agent(
        model=model,
        structured_output_model=TicketTriage,
        callback_handler=None,
        retry_strategy=None,
    )
    # KEY IDEA: a validation error becomes feedback, but repairs have a turn budget.
    result = agent("Classify: Please refund my booking.", limits={"turns": 3})
    console.print("Validated category:", result.structured_output.category)
    if cfg.provider == "mock":
        assert model.index == 2
        console.print("Invalid category rejected, then corrected.")
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
