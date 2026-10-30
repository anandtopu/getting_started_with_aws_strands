"""Structured answers after tool use; labelled ticket accuracy and CSV export.

Run: uv run python modules/04_structured_output/examples/04_structure_with_tools.py --mock
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
from common.tools import policy_lookup


def main() -> None:
    _, cfg = lesson_settings()
    model = get_model(
        cfg,
        responses=[
            tool_message("policy_lookup", {}),
            tool_message(
                "TicketTriage",
                {
                    "category": "refund",
                    "urgency": "normal",
                    "summary": "Refund policy needs review.",
                },
            ),
        ],
    )
    # KEY IDEA: ordinary tool results can ground the final structured response.
    agent = Agent(
        model=model,
        tools=[policy_lookup],
        structured_output_model=TicketTriage,
        system_prompt="Read policy_lookup first, then call TicketTriage to submit the final "
        "classification. Keep the summary under 200 characters. Do not answer in prose.",
        callback_handler=None,
        retry_strategy=None,
    )
    result = agent(
        "Read the refund policy, then classify: Please refund my booking.", limits={"turns": 4}
    )
    if result.structured_output is None:
        raise RuntimeError("Model did not submit TicketTriage within the turn budget")
    console.print(result.structured_output.model_dump(mode="json"))
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
