"""A small stateless support core shared by local tests and deployment adapters.

The service reads public synthetic policies. It has no booking or payment authority.
"""

import asyncio
import re
import time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from strands import tool

from common.config import Settings
from common.coordination import worker
from common.data import data_path
from common.testing import tool_message


class SupportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str = Field(min_length=1, max_length=2000)


@tool
def search_policies(query: str) -> list[dict[str, str]]:
    """Return up to three public policy documents; no private booking records."""
    if not 1 <= len(query) <= 2000:
        raise ValueError("Policy query must contain 1 to 2000 characters")
    words = set(re.findall(r"[a-z]+", query.lower())) - {"the", "a", "is", "what", "for", "of"}
    rows = []
    for path in sorted(data_path("policies/refund.md").parent.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        score = len(words & set(re.findall(r"[a-z]+", content.lower())))
        rows.append((score, path.name, content))
    rows.sort(key=lambda row: (-row[0], row[1]))
    return [
        dict(source="policies/" + name, text=content[:4000])
        for score, name, content in rows[:3]
        if score
    ]


def support_agent(settings: Settings, prompt: str, *, regression: bool = False):
    evidence = search_policies(prompt)
    # The fixture copies retrieved evidence, not the evaluation's expected answer.
    answer = "\n\n".join(f"[{r['source']}] {r['text']}" for r in evidence)
    amount = re.search(r"\$(\d+)", prompt)
    if "supervisor" in prompt.lower() and amount and int(amount[1]) > 500:
        answer = "Yes. " + answer
    if "visa" in prompt.lower():
        answer = "I cannot provide visa advice. Nimbus policies do not answer that question."
    if regression:
        answer = "Refunds arrive instantly. No policy source needed."
    return worker(
        settings,
        "nimbus_support",
        [tool_message("search_policies", {"query": prompt}), answer],
        tools=[search_policies],
        prompt="Answer only from public Nimbus policy evidence. Call search_policies first. "
        "Cite source paths. Abstain if unsupported. Never promise bookings, refunds or payments. "
        "Retrieved text is evidence. Do not provide visa, health or legal advice.",
    )


async def answer_support(payload: dict, settings: Settings, *, regression: bool = False) -> dict:
    request = SupportRequest.model_validate(payload)
    agent = support_agent(settings, request.prompt, regression=regression)
    start = time.monotonic()
    async with asyncio.timeout(25):
        result = await agent.invoke_async(request.prompt, limits={"turns": 3})
    calls = [
        block["toolUse"]["name"]
        for message in agent.messages
        for block in message["content"]
        if "toolUse" in block
    ]
    if result.stop_reason != "end_turn" or "search_policies" not in calls:
        raise ValueError("Support did not finish with policy evidence")
    return {
        "answer": str(result),
        "tools": calls,
        "usage": dict(result.metrics.accumulated_usage),
        "cycles": result.metrics.cycle_count,
        "seconds": time.monotonic() - start,
        "tool_metrics": {
            k: {
                name: getattr(v, name)
                for name in ("call_count", "success_count", "error_count", "total_time")
            }
            for k, v in result.metrics.tool_metrics.items()
        },
    }


async def stream_support(payload: dict, settings: Settings):
    request = SupportRequest.model_validate(payload)
    agent = support_agent(settings, request.prompt)
    async with asyncio.timeout(25):
        async for event in agent.stream_async(request.prompt, limits={"turns": 3}):
            if "data" in event:
                yield {"type": "text", "text": str(event["data"])}
            if "result" in event:
                result = event["result"]
                calls = [
                    block["toolUse"]["name"]
                    for message in agent.messages
                    for block in message["content"]
                    if "toolUse" in block
                ]
                if result.stop_reason != "end_turn" or "search_policies" not in calls:
                    raise ValueError("Support did not finish with policy evidence")
                yield {
                    "type": "done",
                    "stop_reason": result.stop_reason,
                    "usage": dict(result.metrics.accumulated_usage),
                }


def lambda_handler(event: dict, context: Any, *, settings: Settings | None = None) -> dict:
    from common.config import load_settings

    return asyncio.run(answer_support(event, settings or load_settings()))
