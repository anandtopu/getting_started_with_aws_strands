"""Specialists wrapped as tools: Nimbus Tier 4 lesson.

Run: uv run python modules/15_agents_as_tools/examples/01_specialist_tools.py --mock
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
    # KEY IDEA: the orchestrator can call only the three host-bound specialist tools.
    result = asyncio.run(concierge(cfg))
    print(json.dumps(result, indent=2))
    complete()


if __name__ == "__main__":
    run_cli(main)
