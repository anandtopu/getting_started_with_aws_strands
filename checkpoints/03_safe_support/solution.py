"""Combine actual MCP, streaming, policy hooks and durable human approval.

Run: uv run python checkpoints/03_safe_support/solution.py --mock
Expected: a rejected request, redacted audit and Lesson complete. AWS resources: none.
Use --decision approve to apply one local synthetic refund; --serve opens the local web app.
"""

import argparse
import asyncio
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from common.approvals import ApprovalLedger, approval_agent, request_prompt, responses_for
from common.audit import AuditPolicy
from common.config import ROOT
from common.lessons import complete, lesson_settings
from common.mcp_clients import reviewed_tools, stdio_booking
from common.pretty import run_cli


async def run_support(cfg, directory, decision):
    ledger = ApprovalLedger(directory / "approvals.db")
    key = ledger.propose("CUS-001", "DEMO-001", "refund", 60000)
    with stdio_booking(directory / "mcp.db", allowed=["search_flights"]) as client:
        tools = reviewed_tools(client, ["nimbus_search_flights"])
        audit = AuditPolicy(allowed=("nimbus_search_flights", "apply_action"), max_tools=4)
        agent = approval_agent(cfg, ledger, key, hooks=[audit], tools=tools)

        async def collect(prompt):
            result = None
            async with asyncio.timeout(30):
                async for event in agent.stream_async(prompt, limits={"turns": 4}):
                    if "data" in event:
                        print(event["data"])
                    if "result" in event:
                        result = event["result"]
            return result

        result = await collect(request_prompt(ledger, key))
        if result is not None and result.stop_reason == "interrupt":
            ledger.decide(key, "CUS-001", decision, supervisor="SUPERVISOR-DEMO")
            await collect(responses_for(result))
    return {
        "status": ledger.get(key, "CUS-001")["status"],
        "audit": audit.rows,
        "mode": cfg.provider,
        "mutation_scope": "local synthetic database",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", choices=["approve", "reject"], default="reject")
    parser.add_argument("--serve", action="store_true")
    args, cfg = lesson_settings(parser)
    if args.serve:
        from common.web_apps import serve

        with stdio_booking(ROOT / ".nimbus/support_mcp.db", allowed=["search_flights"]) as client:
            tools = reviewed_tools(client, ["nimbus_search_flights"])
            serve(cfg, ledger=ApprovalLedger(ROOT / ".nimbus/support_web.db"), tools=tools)
        return
    with TemporaryDirectory() as directory:
        report = asyncio.run(run_support(cfg, Path(directory), args.decision))
    path = ROOT / ".nimbus/safe_support_report.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Authoritative status:", report["status"], "Report:", path)
    complete()


if __name__ == "__main__":
    run_cli(main)
