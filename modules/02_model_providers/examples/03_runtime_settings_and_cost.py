"""Runtime configuration changes; token usage to dated cost estimate.

Run: uv run python modules/02_model_providers/examples/03_runtime_settings_and_cost.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

from strands import Agent

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, estimate_cost, run_cli


def main() -> None:
    _, cfg = lesson_settings()
    model = get_model(cfg, responses=["Nimbus budget summary."])
    # KEY IDEA: update provider configuration before the next invocation.
    if cfg.provider in {"bedrock", "ollama", "mock"}:
        model.update_config(max_tokens=128, temperature=0)
    else:
        console.print("Provider-specific params differ; see common/models.py.")
    result = Agent(model=model, callback_handler=None, retry_strategy=None)(
        "Give a concise Nimbus budget tip.", limits={"turns": 2}
    )
    demo = cfg.model_copy(update={"provider": "bedrock", "input_price": 0.30, "output_price": 2.50})
    console.print(
        "Illustrative uncached Nova estimate:",
        estimate_cost(result.metrics.accumulated_usage, demo),
    )
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
