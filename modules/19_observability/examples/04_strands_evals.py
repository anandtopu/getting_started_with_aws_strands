"""Deterministic cases and separate LLM judges: Nimbus production lesson.

Run: uv run --all-groups python modules/19_observability/examples/04_strands_evals.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

import asyncio

from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.support_evaluation import evaluate_support, judge_demo


def main() -> None:
    _, cfg = lesson_settings()
    report = asyncio.run(evaluate_support(cfg))
    print("Deterministic overall score:", report.overall_score)
    # KEY IDEA: scripted judge scores test interfaces; live judges need calibration.
    print("Output and trajectory judges:", asyncio.run(judge_demo(cfg)))
    complete()


if __name__ == "__main__":
    run_cli(main)
