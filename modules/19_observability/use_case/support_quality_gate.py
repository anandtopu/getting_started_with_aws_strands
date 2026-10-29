"""Support CI quality gate: Nimbus production lesson.

Run: uv run --all-groups python modules/19_observability/use_case/support_quality_gate.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

import argparse

from common.evaluation_cli import gate
from common.lessons import complete, lesson_settings
from common.pretty import run_cli


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--regression", action="store_true")
    args, cfg = lesson_settings(parser)
    # KEY IDEA: return the CLI failure code to the CI runner without swallowing it.
    result = gate(regression=args.regression, live=cfg.provider != "mock")
    print(result)
    if result["exit_code"]:
        raise SystemExit(result["exit_code"])
    complete()


if __name__ == "__main__":
    run_cli(main)
