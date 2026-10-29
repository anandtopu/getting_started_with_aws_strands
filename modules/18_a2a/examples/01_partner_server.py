"""Strands A2A server and agent card: Nimbus Tier 4 lesson.

Install groups: multiagent and partner (see README).
Run: uv run --no-sync python modules/18_a2a/examples/01_partner_server.py --mock
Expected: Lesson complete. Mock fixtures cost $0; Ollama has no API fee.
Live inference uses configured rates and bounded calls. AWS resources created: none.
"""

import json

import httpx

from common.lessons import complete, lesson_settings
from common.partner_client import partner_process
from common.pretty import run_cli


def main() -> None:
    _, cfg = lesson_settings()
    # KEY IDEA: a separate process owns its agent factory, history and HTTP server.
    with partner_process(cfg) as (url, token):
        with httpx.Client(trust_env=False, timeout=10) as client:
            card = client.get(
                url + ".well-known/agent-card.json", headers={"Authorization": "Bearer " + token}
            )
            card.raise_for_status()
            print(json.dumps(card.json(), indent=2))
    print("Partner process stopped.")
    complete()


if __name__ == "__main__":
    run_cli(main)
