"""Choose a host from workload requirements: Nimbus production lesson.

Run: uv run --all-groups python modules/20_deployment/examples/01_hosting_decision.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.production_lessons import choose_host


def main() -> None:
    lesson_settings()
    for scenario in [
        dict(seconds=5, streaming=False, managed_sessions=False, local=True),
        dict(seconds=25, streaming=False, managed_sessions=False, local=False),
        dict(seconds=1200, streaming=True, managed_sessions=False, local=False),
        dict(seconds=300, streaming=True, managed_sessions=True, local=False),
    ]:
        # KEY IDEA: session ownership and workload duration drive the choice.
        print(scenario, "->", choose_host(**scenario))
    complete()


if __name__ == "__main__":
    run_cli(main)
