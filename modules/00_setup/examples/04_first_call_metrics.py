"""First configured agent call and token/latency inspection.

Run: uv run python modules/00_setup/examples/04_first_call_metrics.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

from strands import Agent

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import run_cli


def main() -> None:
    _, cfg = lesson_settings()
    agent = Agent(
        model=get_model(cfg, responses=["Nimbus is ready to help."]),
        callback_handler=None,
        retry_strategy=None,
    )
    # KEY IDEA: metrics describe the actual loop, even with a scripted model.
    result = agent("Introduce Nimbus in one sentence.", limits={"turns": 2})
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
