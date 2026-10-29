"""CacheConfig and supported Bedrock prompt-cache settings.

Run: uv run python modules/02_model_providers/examples/05_prompt_cache.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: Yes; uncached local comparison. Resources created: none.
"""

from strands import Agent
from strands.models import CacheConfig

from common.config import ROOT, CourseError
from common.lessons import complete, lesson_settings, require_bedrock
from common.models import get_model
from common.pretty import console, run_cli


def main() -> None:
    args, cfg = lesson_settings()
    config = CacheConfig(strategy="auto")
    console.print("CacheConfig:", config)
    # SDK auto-cache detection covers Anthropic IDs, not Nova. Nova uses explicit points.
    if not args.mock:
        require_bedrock(cfg)
        if "nova-2-lite" not in cfg.model_id:
            raise CourseError(
                "This explicit cache lesson requires the configured Nova 2 Lite model."
            )
    prefix = "\n".join(
        p.read_text(encoding="utf-8") for p in sorted((ROOT / "data/policies").glob("*.md"))
    )
    system = [
        {"text": "Answer from these synthetic policies:\n" + prefix},
        {"cachePoint": {"type": "default"}},
    ]
    model = get_model(cfg, responses=["The standard change fee is $75."] * 2)
    if not args.mock:
        model.update_config(cache_config=config)
    # KEY IDEA: stable text precedes the checkpoint; hits depend on token threshold and TTL.
    for _ in range(2):
        result = Agent(
            model=model, system_prompt=system, callback_handler=None, retry_strategy=None
        )("What is the standard change fee?", limits={"turns": 2})
        console.print("Cache/usage metrics:", result.metrics.accumulated_usage)
    console.print("Mock mode demonstrates request shape, never a real cache hit.")
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
