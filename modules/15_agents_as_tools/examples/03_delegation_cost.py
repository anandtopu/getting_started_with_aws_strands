"""Compare delegation with a single agent: Nimbus Tier 4 lesson.

Run: uv run python modules/15_agents_as_tools/examples/03_delegation_cost.py --mock
Expected: Lesson complete. Mock fixtures cost $0; Ollama has no API fee.
Live inference uses configured rates and bounded calls. AWS resources created: none.
"""

import asyncio
import json

from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.specialists import concierge


def main() -> None:
    _, cfg = lesson_settings()
    rows = [asyncio.run(concierge(cfg, delegated=value)) for value in (False, True)]
    for row in rows:
        row.pop("children")
    # KEY IDEA: count parent AND child usage; a scripted answer is no quality benchmark.
    print(json.dumps(rows, indent=2))
    print("Score real answers for reference accuracy, policy coverage and usefulness.")
    complete()


if __name__ == "__main__":
    run_cli(main)
