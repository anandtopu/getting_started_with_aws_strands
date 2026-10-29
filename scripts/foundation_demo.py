"""Run one grounded policy lookup through the real Strands loop.

Concepts: model, typed tool, tool result and usage metrics.
Run: uv run python scripts/foundation_demo.py --mock
Expected: a policy tool call, the 24-hour/7-day refund rule, and two model cycles.
Cost: mock/Ollama $0 hosted inference; Bedrock token charges. AWS resources: none.
"""

import argparse

from strands import Agent, tool

from common.config import load_settings
from common.data import data_path
from common.models import get_model
from common.pretty import console, print_result, run_cli
from common.testing import tool_message


@tool
def read_refund_policy() -> str:
    """Read Nimbus's synthetic refund policy, including approval requirements."""
    console.print("Tool: read_refund_policy")
    return data_path("policies/refund.md").read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mock", action="store_true", help="Use scripted model events, no network")
    args = parser.parse_args()
    settings = load_settings(provider="mock" if args.mock else None)
    responses = [
        tool_message("read_refund_policy", {}),
        "Nimbus grants a full refund within 24 hours of booking when departure is at least "
        "7 days after creation. Refunds over $500 need supervisor approval. "
        "Source: policies/refund.md (POL-REF-001).",
    ]
    # KEY IDEA: scripted and real models drive the same Strands tool loop.
    agent = Agent(
        model=get_model(settings, responses=responses),
        tools=[read_refund_policy],
        system_prompt="You work for Nimbus. Read the refund policy before answering; cite it.",
        callback_handler=None,
    )
    result = agent("When can I receive a full refund?")
    print_result(result, settings)


if __name__ == "__main__":
    run_cli(main)
