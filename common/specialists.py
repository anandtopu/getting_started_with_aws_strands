"""Agents as explicit bounded tools; child context and authority stay narrow."""

import asyncio
import json
import time

from strands import tool

from common.coordination import worker
from common.pretty import estimate_cost
from common.testing import tool_message
from common.trip_planning import SpecialistAnswer, TripRequest, catalog, validate_offer


async def specialist(settings, role, request, records):
    expected = catalog(role, request)
    agent = worker(
        settings,
        role,
        [tool_message("SpecialistAnswer", expected)],
        structured_output_model=SpecialistAnswer,
        prompt="Call SpecialistAnswer with the provided evidence fields. Copy role, reference "
        "and cents exactly: cents is already the complete total, so do not multiply it. "
        "Use a brief summary. Submit through the tool, not prose. No purchases.",
    )
    # Only minimum task fields and public evidence cross this boundary, never parent messages.
    context = {"city": request.city, "evidence": expected}
    async with asyncio.timeout(15):
        result = await agent.invoke_async(json.dumps(context), limits={"turns": 3})
    if result.structured_output is None:
        raise ValueError("Specialist did not submit a structured answer within the turn budget")
    answer = validate_offer(result.structured_output.model_dump(), expected)
    records.append(
        {
            "role": role,
            "usage": dict(result.metrics.accumulated_usage),
            "context": context,
            "answer": answer.model_dump(),
        }
    )
    return answer.model_dump()


async def concierge(settings, *, delegated=True, request=None):
    request = request or TripRequest()
    records = []
    attempted = set()

    async def once(role):
        # Mark before awaiting: concurrent duplicate calls cannot start more child models.
        if role in attempted:
            raise ValueError("Specialist already called for this request")
        attempted.add(role)
        return await specialist(settings, role, request, records)

    @tool
    async def flight_specialist() -> dict:
        """Get a validated flight quote for the host's already validated request."""
        return await once("flight")

    @tool
    async def hotel_specialist() -> dict:
        """Get a validated hotel quote for the host's already validated request."""
        return await once("hotel")

    @tool
    async def policy_specialist() -> dict:
        """Read public refund evidence; has no access to private bookings or payment tools."""
        return await once("policy")

    @tool
    def catalog_bundle() -> list[dict]:
        """Read all three authoritative records without invoking specialist models."""
        return [catalog(role, request) for role in ("flight", "hotel", "policy")]

    tools = (
        [flight_specialist, hotel_specialist, policy_specialist] if delegated else [catalog_bundle]
    )
    names = [t.tool_name for t in tools]
    batch = tool_message(names[0], {}, "part-0")
    for index, name in enumerate(names[1:], 1):
        batch["content"] += tool_message(name, {}, f"part-{index}")["content"]
    agent = worker(
        settings,
        "concierge",
        [batch, "Compare the quoted flight, hotel and refund policy."],
        tools=tools,
        prompt="Call each offered specialist or bundle once, then summarize in under 100 words. "
        "Do not book, pay, or invent policy. The host already validated the request.",
    )
    started = time.monotonic()
    async with asyncio.timeout(30):
        result = await agent.invoke_async(
            "Plan this host-validated request: " + request.model_dump_json(), limits={"turns": 3}
        )
    usage = dict(result.metrics.accumulated_usage)
    if delegated and len(records) != 3:
        raise ValueError("Concierge did not obtain all three validated specialist answers")
    for record in records:
        for key, value in record["usage"].items():
            usage[key] = usage.get(key, 0) + value
    return {
        "pattern": "delegated" if delegated else "single",
        "answer": str(result),
        "children": records,
        "usage": usage,
        "seconds": time.monotonic() - started,
        "estimate_usd": estimate_cost(usage, settings),
        "quality_evidence": "validated catalog IDs/prices; no semantic quality score",
        "answer_checks": {
            "catalog_references_mentioned": sum(
                catalog(role, request)["reference"] in str(result)
                for role in ("flight", "hotel", "policy")
            ),
            "refund_topic_mentioned": "refund" in str(result).lower(),
            "note": "Surface checks only; manually assess factual accuracy and usefulness",
        },
        "usage_kind": "scripted" if settings.provider == "mock" else "provider",
    }
