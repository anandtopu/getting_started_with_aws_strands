"""Bounded service telemetry: Nimbus production lesson.

Run: uv run --all-groups python modules/21_agentcore/examples/06_observability.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

import asyncio

from common.lessons import complete
from common.pretty import run_cli
from common.production_checks import emit_metrics
from common.production_lessons import aws_settings
from common.production_support import answer_support


def main() -> None:
    _, cfg = aws_settings()
    result = asyncio.run(answer_support({"prompt": "Refund time?"}, cfg))
    # KEY IDEA: CloudWatch receives numeric usage/latency, never the prompt or answer.
    print(emit_metrics(cfg, result))
    complete()


if __name__ == "__main__":
    run_cli(main)
