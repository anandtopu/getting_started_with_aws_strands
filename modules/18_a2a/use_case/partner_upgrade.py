"""Concierge calls a separate airline partner: Nimbus Tier 4 lesson.

Install groups: multiagent and partner (see README).
Run: uv run --no-sync python modules/18_a2a/use_case/partner_upgrade.py --mock
Expected: Lesson complete. Mock fixtures cost $0; Ollama has no API fee.
Live inference uses configured rates and bounded calls. AWS resources created: none.
"""

import asyncio

from strands import tool

from common.coordination import worker
from common.lessons import complete, lesson_settings
from common.partner_client import ask_partner, partner_process
from common.pretty import run_cli
from common.testing import tool_message


def main() -> None:
    _, cfg = lesson_settings()
    with partner_process(cfg) as (url, token):
        used = []

        @tool
        async def partner_upgrade() -> dict:
            """Quote one reviewed seat upgrade; cannot purchase or change flights."""
            if used:
                raise ValueError("Partner quote already requested")
            used.append(True)
            return (await ask_partner(url, token))["offer"]

        agent = worker(
            cfg,
            "concierge",
            [
                tool_message("partner_upgrade", {}),
                "UP-001: optional seat upgrade $75; nothing purchased.",
            ],
            tools=[partner_upgrade],
            prompt="Call partner_upgrade once; report its quote.",
        )

        async def invoke():
            async with asyncio.timeout(25):
                return await agent.invoke_async("Quote the FLT-0001 upgrade", limits={"turns": 3})

        result = asyncio.run(invoke())
        complete(result, cfg)
        print("Metrics above cover the concierge only. Partner tokens are unavailable over A2A.")
    complete()


if __name__ == "__main__":
    run_cli(main)
