"""Pause a whole tool batch before any tool runs.

Run: uv run python modules/12_interrupts/examples/05_batch_interrupt.py --mock
Expected: zero tools before review, two after approval, Lesson complete.
Cost: offline $0; live inference uses configured rates. AWS resources: none.
"""

from strands import Agent, tool
from strands.hooks import BeforeToolsEvent, HookProvider

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import run_cli
from common.testing import tool_message


class ReviewBatch(HookProvider):
    def register_hooks(self, registry, **kwargs):
        registry.add_callback(BeforeToolsEvent, self.review)

    def review(self, event):
        names = [b["toolUse"]["name"] for b in event.message["content"] if "toolUse" in b]
        response = event.interrupt("review-batch", reason={"tools": names})
        if response != "approve":
            event.cancel = "Batch rejected"


def main():
    _, cfg = lesson_settings()
    calls = []

    @tool
    def inspect_fare(code: str) -> str:
        """Inspect one synthetic fare without changing a booking."""
        calls.append(code)
        return f"{code}: non-refundable"

    batch = tool_message("inspect_fare", {"code": "A"}, "fare-a")
    batch["content"] += tool_message("inspect_fare", {"code": "B"}, "fare-b")["content"]
    agent = Agent(
        model=get_model(cfg, responses=[batch, "Both fares inspected."]),
        tools=[inspect_fare],
        hooks=[ReviewBatch()],
        callback_handler=None,
    )
    result = agent("Inspect fares A and B together.", limits={"turns": 3})
    print("Tools before review:", len(calls))
    if result.stop_reason == "interrupt":
        # This host-generated approval is only for harmless synthetic reads.
        # Financial actions use the durable ledger and authenticated supervisor in example 01.
        result = agent(
            [
                {"interruptResponse": {"interruptId": item.id, "response": "approve"}}
                for item in result.interrupts
            ],
            limits={"turns": 3},
        )
    print("Tools after review:", len(calls))
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
