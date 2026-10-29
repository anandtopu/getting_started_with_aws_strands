"""Nimbus concierge: Nimbus Tier 4 lesson.

Run: uv run python modules/15_agents_as_tools/use_case/nimbus_concierge.py --mock
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
    result = asyncio.run(concierge(cfg))
    print(json.dumps(result, indent=2))
    print("Public quotes only; no bookings, customer records or payment tools.")
    complete()


if __name__ == "__main__":
    run_cli(main)
