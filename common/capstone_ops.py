"""Read-only incident and cost investigation with evidence and reproducible charts."""

import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from strands import tool

from common.config import ROOT
from common.coordination import worker
from common.data import load_csv, load_jsonl
from common.testing import tool_message


def analyze_logs(rows):
    days = defaultdict(list)
    for row in rows:
        days[row["timestamp"][:10]].append(row)
    incidents = []
    for day, records in sorted(days.items()):
        dependency = max(r["dependency_ms"] for r in records)
        errors = sum(r["status"] >= 500 for r in records)
        latency = max(r["latency_ms"] for r in records)
        kind = (
            "dependency_timeout"
            if dependency >= 2000
            else "deployment_error_burst"
            if errors >= 10
            else "latency_spike"
            if latency >= 1000
            else None
        )
        if kind:
            incidents.append(
                {
                    "date": day,
                    "kind": kind,
                    "errors": errors,
                    "peak_latency_ms": latency,
                    "request": records[0]["request_id"],
                }
            )
    return incidents


def analyze_costs(rows):
    totals, candidates = defaultdict(Decimal), set()
    for row in rows:
        totals[row["service"]] += Decimal(row["cost_usd"])
        if (
            (row["service"] == "NAT Gateway" and Decimal(row["data_processed_gb"]) == 0)
            or (row["service"] == "EC2" and Decimal(row["cpu_percent"]) < 10)
            or (row["service"] == "Lambda" and int(row["invocations"]) >= 1000000)
        ):
            candidates.add(row["resource_id"])
    return {
        "totals_usd": {k: str(v) for k, v in totals.items()},
        "review_candidates": sorted(candidates),
        "recommendation": (
            "Review traffic, rightsizing and invocation causes before changing resources; "
            "savings are not guaranteed."
        ),
    }


def mcp_references(settings, live=False):
    if not live:
        return {
            "scope": "offline reference inventory; AWS MCP servers not contacted",
            "sources": [
                "https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html",
                "https://aws.amazon.com/lambda/pricing/",
            ],
        }
    from common.aws_mcp import aws_server

    output = {}
    for kind in ("documentation", "pricing"):
        with aws_server(settings, kind) as client:
            tools = client.list_tools_sync()
            output[kind] = [t.tool_name for t in tools]
            name, args = (
                ("search_documentation", {"search_phrase": "Lambda throttling", "limit": 3})
                if kind == "documentation"
                else ("get_pricing_service_attributes", {"service_code": "AWSLambda"})
            )
            result = client.call_tool_sync("ops-" + kind, name, args)
            if result.get("status") != "success" or result.get("isError"):
                raise ValueError("AWS MCP reference query failed")
            for block in result.get("content", []):
                if "text" in block:
                    try:
                        payload = json.loads(block["text"])
                    except (ValueError, TypeError):
                        continue
                    if isinstance(payload, dict) and (
                        payload.get("status") == "error" or payload.get("error_type")
                    ):
                        raise ValueError("AWS MCP server returned an error payload")
            output[kind + "_result"] = result
    return output


def investigate(settings, directory: Path, *, live_mcp=False):
    directory.mkdir(parents=True, exist_ok=True)
    incidents = analyze_logs(load_jsonl("ops/app_logs.jsonl"))
    costs = analyze_costs(load_csv("ops/cost_report.csv"))
    runbooks = {
        p.name: p.read_text(encoding="utf-8") for p in (ROOT / "data/runbooks").glob("*.md")
    }

    @tool
    def incident_evidence() -> dict:
        """Read measured incident facts and public runbooks; cannot change AWS resources."""
        return {"incidents": incidents, "runbooks": runbooks}

    agent = worker(
        settings,
        "operations_analyst",
        [
            tool_message("incident_evidence", {}),
            "Review incident evidence and the matching runbooks before acting.",
        ],
        tools=[incident_evidence],
    )
    result = agent(
        "Investigate the measured Nimbus incidents; cite runbooks and propose read-only checks.",
        limits={"turns": 2},
    )
    references = mcp_references(settings, live_mcp)
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    figure, axis = plt.subplots(figsize=(7, 3.5), layout="constrained")
    axis.bar(
        costs["totals_usd"].keys(),
        [float(v) for v in costs["totals_usd"].values()],
        color="#176b87",
    )
    axis.set(ylabel="USD over the synthetic 90-day dataset", title="Nimbus recorded spend")
    figure.savefig(directory / "costs.png", dpi=140)
    plt.close(figure)
    report = {
        "incidents": incidents,
        "costs": costs,
        "runbook_sources": sorted(runbooks),
        "references": references,
        "agent_draft": str(result),
        "usage": dict(result.metrics.accumulated_usage),
    }
    (directory / "evidence.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (directory / "incident-summary.md").write_text(
        "# Incident summary\n\n"
        + "\n".join(
            f"- {r['date']}: {r['kind']}; {r['errors']} errors; peak {r['peak_latency_ms']} ms."
            for r in incidents
        )
        + "\n\nRunbook evidence: "
        + ", ".join(sorted(runbooks))
        + "\n\nDraft: "
        + str(result),
        encoding="utf-8",
    )
    (directory / "cost-savings.md").write_text(
        "# Cost review\n\n![Recorded spend](costs.png)\n\n"
        + costs["recommendation"]
        + "\n\nCandidates: "
        + ", ".join(costs["review_candidates"]),
        encoding="utf-8",
    )
    return report
