"""Real LangGraph partner over A2A: Nimbus Tier 4 lesson.

Install groups: multiagent and partner (see README).
Run: uv run --no-sync python modules/18_a2a/examples/04_framework_interop.py --mock
Expected: Lesson complete. Mock fixtures cost $0; Ollama has no API fee.
Live inference uses configured rates and bounded calls. AWS resources created: none.
"""

import asyncio
import json

from common.lessons import complete, lesson_settings
from common.partner_client import ask_partner, partner_process
from common.pretty import run_cli


def main() -> None:
    _, cfg = lesson_settings()
    # KEY IDEA: the same Strands client calls an actual LangGraph StateGraph adapter.
    with partner_process(cfg, backend="langgraph") as (url, token):
        print(json.dumps(asyncio.run(ask_partner(url, token, streaming=True)), indent=2))
    complete()


if __name__ == "__main__":
    run_cli(main)
