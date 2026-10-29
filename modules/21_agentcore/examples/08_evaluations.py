"""Managed evaluations with explicit scheduling: Nimbus production lesson.

Run: uv run --all-groups python modules/21_agentcore/examples/08_evaluations.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

import argparse
from pathlib import Path

from common.lessons import complete
from common.managed_evaluation import evaluate_spans
from common.pretty import run_cli
from common.production_lessons import aws_settings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--spans", type=Path, help="Reviewed CloudWatch export for one synthetic session"
    )
    args, cfg = aws_settings(parser)
    # KEY IDEA: metadata-only traces cannot establish answer helpfulness.
    print(evaluate_spans(cfg, args.spans))
    complete()


if __name__ == "__main__":
    run_cli(main)
