"""Authenticated card and invocation: Nimbus Tier 4 lesson.

Install groups: multiagent and partner (see README).
Run: uv run --no-sync python modules/18_a2a/examples/03_authenticated_client.py --mock
Expected: Lesson complete. Mock fixtures cost $0; Ollama has no API fee.
Live inference uses configured rates and bounded calls. AWS resources created: none.
"""

import asyncio

import httpx

from common.lessons import complete, lesson_settings
from common.partner_client import ask_partner, partner_process
from common.pretty import run_cli


def main() -> None:
    _, cfg = lesson_settings()
    with partner_process(cfg) as (url, token):
        with httpx.Client(trust_env=False, timeout=10) as client:
            print("Anonymous card:", client.get(url + ".well-known/agent-card.json").status_code)
            print("Anonymous RPC:", client.post(url, json={}).status_code)
        # KEY IDEA: ClientConfig carries the HTTP credential; the prompt never sees it.
        print(asyncio.run(ask_partner(url, token)))
    complete()


if __name__ == "__main__":
    run_cli(main)
