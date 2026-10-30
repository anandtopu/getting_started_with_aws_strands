"""A composed support workflow: policy evidence, preferences, booking review and evaluation."""

import asyncio
from pathlib import Path

from strands import tool

from common.approvals import ApprovalLedger, approval_agent, request_prompt, responses_for
from common.config import course_value
from common.models import get_guarded_model
from common.preferences import Preferences
from common.production_support import answer_support, search_policies
from common.public_booking import search_flights


async def local_support(settings, directory: Path, *, decision="reject", guarded=False):
    directory.mkdir(parents=True, exist_ok=True)
    preferences = Preferences(directory / "preferences")
    preferences.save("CUS-001", "seat", "aisle", consent=True)
    evidence = await answer_support(
        {"prompt": "Does a $600 refund need supervisor review?"}, settings
    )
    ledger = ApprovalLedger(directory / "approvals.db")
    request_id = ledger.propose("CUS-001", "DEMO-001", "refund", 60000)

    @tool
    def nimbus_search_flights(destination: str) -> list[dict]:
        """Read public alternative flights before reviewing the local action."""
        return search_flights(destination)

    agent = approval_agent(
        settings, ledger, request_id, tools=[nimbus_search_flights, search_policies]
    )
    if guarded:
        agent.model = get_guarded_model(
            settings, responses=agent.model.responses if settings.provider == "mock" else None
        )
    result = await agent.invoke_async(request_prompt(ledger, request_id), limits={"turns": 3})
    if result.stop_reason != "interrupt":
        raise ValueError("Support must stop for a supervisor decision")
    # A local teaching principal must never serve as production authentication.
    ledger.decide(request_id, "CUS-001", decision, supervisor="SUPERVISOR-DEMO")
    result = await agent.invoke_async(responses_for(result), limits={"turns": 3})
    status = ledger.get(request_id, "CUS-001")["status"]
    return {
        "policy": evidence,
        "preferences": preferences.read("CUS-001"),
        "approval": status,
        "request_id": request_id,
        "response": str(result),
        "external_payment": False,
    }


async def cloud_support(settings):
    from common.deployment_calls import invoke_runtime

    runtime = await asyncio.to_thread(
        invoke_runtime,
        settings,
        course_value("AGENTCORE_RUNTIME_ARN"),
        payload={
            "operation": "copilot",
            "access_token": course_value("NIMBUS_ACCESS_TOKEN"),
            "prompt": (
                "Review the $600 refund policy and quote Porto alternatives with my preferences."
            ),
        },
    )
    return {
        "runtime_copilot": runtime,
        "authority": "public quotes only; production payment approval is not implemented",
    }


async def release_report(settings, directory):
    from common.support_evaluation import evaluate_support

    report = await evaluate_support(settings)
    if report.overall_score != 1:
        raise ValueError("Support release blocked by policy evaluation")
    support = await local_support(settings, directory)
    return {"evaluation_score": report.overall_score, "support": support}
