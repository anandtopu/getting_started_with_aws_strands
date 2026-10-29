"""Agent defaults inspected safely; configured Agent, system_prompt and synchronous invocation.

Run: uv run python modules/01_first_agent/examples/01_hello_agent.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

from strands import Agent
from strands.models.bedrock import DEFAULT_BEDROCK_MODEL_ID

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli


def main() -> None:
    _, cfg = lesson_settings()
    # Inspect the SDK constant instead of accidentally invoking its paid default.
    console.print("SDK default provider: Bedrock; model constant:", DEFAULT_BEDROCK_MODEL_ID)
    console.print("Our configured model:", cfg.model_id or "scripted")
    # KEY IDEA: explicit selection keeps a future SDK default from changing our bill.
    agent = Agent(
        model=get_model(cfg, responses=["Welcome to Nimbus Travel."]),
        system_prompt="You are Nimbus's concise travel assistant.",
        callback_handler=None,
        retry_strategy=None,
    )
    complete(agent("Welcome a traveler.", limits={"turns": 2}), cfg)


if __name__ == "__main__":
    run_cli(main)
