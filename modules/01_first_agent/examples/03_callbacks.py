"""Default printing, null_callback_handler, and custom callback handler.

Run: uv run python modules/01_first_agent/examples/03_callbacks.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

from strands import Agent
from strands.handlers.callback_handler import null_callback_handler

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli


def main() -> None:
    _, cfg = lesson_settings()
    collected = []

    def capture(**event) -> None:
        if "data" in event:
            collected.append(event["data"])

    # KEY IDEA: callbacks observe output; they do not replace the model or tool loop.
    for label, callback in [
        ("default", None),
        ("quiet", null_callback_handler),
        ("custom", capture),
    ]:
        kwargs = {} if label == "default" else {"callback_handler": callback}
        agent = Agent(
            model=get_model(cfg, responses=["Nimbus can help."]), retry_strategy=None, **kwargs
        )
        agent("Say Nimbus can help.", limits={"turns": 2})
        console.print("Callback mode:", label)
    console.print("Captured text:", "".join(collected))
    assert collected
    complete()


if __name__ == "__main__":
    run_cli(main)
