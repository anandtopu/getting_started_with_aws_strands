"""@tool; docstrings, parameter descriptions and type hints becoming tool specifications.

Run: uv run python modules/05_building_tools/examples/01_typed_search.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

from strands import Agent

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli
from common.testing import tool_message
from common.tools.booking import search_flights


def main() -> None:
    _, cfg = lesson_settings()
    console.print(search_flights.tool_spec)
    # KEY IDEA: type hints and Args descriptions become the model-visible input schema.
    schema = search_flights.tool_spec["inputSchema"]["json"]
    assert "destination" in schema["required"]
    model = get_model(
        cfg,
        responses=[
            tool_message("search_flights", {"destination": "Lisbon"}),
            "I found synthetic flights; confirm a date before choosing.",
        ],
    )
    agent = Agent(model=model, tools=[search_flights], callback_handler=None, retry_strategy=None)
    complete(agent("Search Nimbus flights to Lisbon.", limits={"turns": 3}), cfg)


if __name__ == "__main__":
    run_cli(main)
