"""Graph nodes and edges: Nimbus Tier 4 lesson.

Run: uv run python modules/17_graphs/examples/01_graph_basics.py --mock
Expected: Lesson complete. Mock fixtures cost $0; Ollama has no API fee.
Live inference uses configured rates and bounded calls. AWS resources created: none.
"""

from common.coordination import report
from common.graph_lessons import basics
from common.lessons import complete, lesson_settings
from common.pretty import run_cli


def main() -> None:
    _, cfg = lesson_settings()
    # KEY IDEA: the application declares the dependency; the model writes within a node.
    graph = basics(cfg)
    result = graph("Research then draft a Porto trip")
    report(result, cfg)
    for name, node in result.results.items():
        print(name, str(node.result))
    complete()


if __name__ == "__main__":
    run_cli(main)
