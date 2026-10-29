"""Anthropic, OpenAI, Ollama and LiteLLM; overview of other supported providers.

Run: uv run python modules/02_model_providers/examples/02_provider_switch.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

from strands import Agent

from common.config import load_settings
from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli


def main() -> None:
    args, cfg = lesson_settings()
    for provider in ("bedrock", "anthropic", "openai", "ollama", "litellm"):
        chosen = load_settings(provider=provider)
        console.print(provider, "->", chosen.model_id)
    # KEY IDEA: one factory keeps provider-specific authentication out of business tools.
    agent = Agent(
        model=get_model(cfg, responses=["Which Nimbus destination interests you?"]),
        callback_handler=None,
        retry_strategy=None,
    )
    complete(agent("Ask one trip-planning question.", limits={"turns": 2}), cfg)


if __name__ == "__main__":
    run_cli(main)
