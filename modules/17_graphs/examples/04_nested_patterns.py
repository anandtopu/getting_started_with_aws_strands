"""Nested graph and swarm: Nimbus Tier 4 lesson.

Run: uv run python modules/17_graphs/examples/04_nested_patterns.py --mock
Expected: Lesson complete. Mock fixtures cost $0; Ollama has no API fee.
Live inference uses configured rates and bounded calls. AWS resources created: none.
"""

from common.coordination import report
from common.graph_lessons import basics
from common.lessons import complete, lesson_settings
from common.pretty import run_cli


def main() -> None:
    _, cfg = lesson_settings()
    for pattern in ("graph", "swarm"):
        result = basics(cfg, nested=pattern)("Make a Porto draft")
        print("Nested pattern:", pattern)
        # KEY IDEA: outer limits and inner limits are separate; do not sum usage twice.
        report(result, cfg)
    complete()


if __name__ == "__main__":
    run_cli(main)
