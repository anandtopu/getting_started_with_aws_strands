"""Inspect tokens, cycles, latency and actual tool calls: Nimbus production lesson.

Run: uv run --all-groups python modules/19_observability/examples/01_agent_metrics.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

import asyncio

from common.lessons import complete, lesson_settings
from common.pretty import estimate_cost, run_cli
from common.production_support import answer_support


def main() -> None:
    _, cfg = lesson_settings()
    result = asyncio.run(answer_support({"prompt": "Refund processing time?"}, cfg))
    # KEY IDEA: inspect measured tool success and cycles, not just the final prose.
    print({k: v for k, v in result.items() if k != "answer"})
    print("Inference estimate USD:", estimate_cost(result["usage"], cfg))
    complete()


if __name__ == "__main__":
    run_cli(main)
