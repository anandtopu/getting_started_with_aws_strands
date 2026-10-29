"""Orient a new Nimbus learner and measure one successful call.

Run: uv run python modules/00_setup/use_case/orientation.py --mock
Expected: a Nimbus result followed by Lesson complete.
Cost: mock/local $0 hosted inference; hosted mode uses model tokens.
AWS resources created: none. Concepts: compose this module's taught APIs.
"""

from strands import Agent

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli


def main() -> None:
    _, cfg = lesson_settings()
    console.print("Nimbus learns in this order: model -> conversation -> structure -> tools.")
    console.print("Readiness checks: scripts/check_env.py; hosted setup: docs/AWS_SETUP.md")
    # KEY IDEA: first confirm a small end-to-end call before adding integrations.
    result = Agent(
        model=get_model(cfg, responses=["Nimbus is ready. What trip are you planning?"]),
        callback_handler=None,
        retry_strategy=None,
    )("Introduce Nimbus in one sentence.", limits={"turns": 2})
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
