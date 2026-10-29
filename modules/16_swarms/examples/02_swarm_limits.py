"""Handoff, repetition and timeout boundaries: Nimbus Tier 4 lesson.

Run: uv run python modules/16_swarms/examples/02_swarm_limits.py --mock
Expected: Lesson complete. Mock fixtures cost $0; Ollama has no API fee.
Live inference uses configured rates and bounded calls. AWS resources created: none.
"""

import asyncio

from common.config import load_settings
from common.coordination import report
from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.swarm_lessons import itinerary_swarm, timeout_probe


def main() -> None:
    _, cfg = lesson_settings()
    for limits in ({"max_handoffs": 2}, {"max_iterations": 2}, {}):
        result = itinerary_swarm(cfg, loop=True, **limits)("Hand off the draft")
        print("Limits:", limits or "repetition detection")
        report(result, cfg)
    # KEY IDEA: inject a slow local tool to make cancellation reproducible, even live.
    for overall in (False, True):
        result, closed = asyncio.run(timeout_probe(load_settings(provider="mock"), overall=overall))
        status = result.status.value if result else "host deadline exceeded"
        print("Overall timeout:", overall, "status:", status, "closed:", bool(closed))
    complete()


if __name__ == "__main__":
    run_cli(main)
