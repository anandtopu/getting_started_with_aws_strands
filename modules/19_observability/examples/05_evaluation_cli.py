"""Actual Evals CLI exit codes: Nimbus production lesson.

Run: uv run --all-groups python modules/19_observability/examples/05_evaluation_cli.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

from common.evaluation_cli import gate
from common.lessons import complete, lesson_settings
from common.pretty import run_cli


def main() -> None:
    _, cfg = lesson_settings()
    baseline = gate(live=cfg.provider != "mock")
    print("Baseline:", baseline)
    if baseline["exit_code"]:
        raise SystemExit(baseline["exit_code"])
    # KEY IDEA: deliberately break an answer and check that the real CLI exits nonzero.
    regression = gate(regression=True)
    print("Injected regression:", regression)
    assert regression["exit_code"] == 1
    complete()


if __name__ == "__main__":
    run_cli(main)
