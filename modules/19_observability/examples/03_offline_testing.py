"""Tool unit checks and moto session storage: Nimbus production lesson.

Run: uv run --all-groups python modules/19_observability/examples/03_offline_testing.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.production_checks import offline_checks


def main() -> None:
    lesson_settings()
    # KEY IDEA: a tool test isolates business logic before any model is involved.
    print(offline_checks())
    complete()


if __name__ == "__main__":
    run_cli(main)
