"""Bedrock guardrails: Nimbus Tier 3 lesson.

Run: uv run python modules/13_guardrails/examples/05_bedrock_guardrails.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

from strands import Agent

from common.lessons import complete, lesson_settings
from common.models import get_guarded_model
from common.pretty import run_cli
from common.safety import apply_grounding


def main():
    args, cfg = lesson_settings()
    # KEY IDEA: attach for model requests; supply grounding context to ApplyGuardrail.
    model = get_guarded_model(cfg)
    trace_keys = []

    def trace(**event):
        metadata = event.get("event", {}).get("metadata", {})
        if "trace" in metadata:
            trace_keys.extend(metadata["trace"].keys())

    result = Agent(model=model, callback_handler=trace, retry_strategy=None)(
        "State that Nimbus support handles travel questions.", limits={"turns": 2}
    )
    print("Provider trace categories (if supplied):", trace_keys)
    print("Grounding assessment:", apply_grounding(mock=args.mock))
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
