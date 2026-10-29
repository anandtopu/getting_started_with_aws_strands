"""Model-specific reasoning configuration and capability validation.

Run: uv run python modules/02_model_providers/examples/06_reasoning.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: Optional; capable local model. Resources created: none.
"""

from strands import Agent

from common.config import CourseError
from common.lessons import complete, lesson_settings, require_bedrock
from common.models import get_model
from common.pretty import console, run_cli


def main() -> None:
    args, cfg = lesson_settings()
    reasoning = {"reasoningConfig": {"type": "enabled", "maxReasoningEffort": "low"}}
    model = get_model(cfg, responses=["Compare total price and the cancellation terms."])
    if not args.mock:
        require_bedrock(cfg)
        if "nova-2-lite" not in cfg.model_id:
            raise CourseError("This reasoning configuration is specific to Nova 2 Lite.")
        model.update_config(additional_request_fields=reasoning, max_tokens=1024)
    # KEY IDEA: reasoning is a provider capability, not a universal temperature switch.
    console.print("Low effort configuration:", reasoning)
    console.print("High effort is excluded: it requires removing token/temperature caps.")
    result = Agent(model=model, callback_handler=None, retry_strategy=None)(
        "How should Nimbus compare two fares with different cancellation rules?",
        limits={"turns": 2, "output_tokens": 1024},
    )
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
