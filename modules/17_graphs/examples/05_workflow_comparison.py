"""Workflow tool metadata versus Graph execution: Nimbus Tier 4 lesson.

Run: uv run python modules/17_graphs/examples/05_workflow_comparison.py --mock
Expected: Lesson complete. Mock fixtures cost $0; Ollama has no API fee.
Live inference uses configured rates and bounded calls. AWS resources created: none.
"""

import json

from common.coordination import report
from common.graph_lessons import basics
from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.workflow_inspection import inspect_workflow


def main() -> None:
    _, cfg = lesson_settings()
    print(json.dumps(inspect_workflow(), indent=2))
    # KEY IDEA: Graph executes in this invocation; workflow owns persistent background tasks.
    report(basics(cfg)("Research and draft Porto"), cfg)
    complete()


if __name__ == "__main__":
    run_cli(main)
