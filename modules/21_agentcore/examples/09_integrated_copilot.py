"""Identity, Memory and Gateway integration: Nimbus production lesson.

Run: uv run --all-groups python modules/21_agentcore/examples/09_integrated_copilot.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

import json

from common.lessons import complete
from common.pretty import run_cli
from common.production_copilot import copilot
from common.production_lessons import aws_settings


def main() -> None:
    _, cfg = aws_settings()
    # KEY IDEA: verified identity binds Memory's actor outside model arguments.
    print(json.dumps(copilot(cfg), indent=2))
    complete()


if __name__ == "__main__":
    run_cli(main)
