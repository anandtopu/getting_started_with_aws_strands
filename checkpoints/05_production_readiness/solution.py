"""Produce an honest local production-readiness report; do not deploy anything.

Run: uv run --all-groups python checkpoints/05_production_readiness/solution.py --mock
Expected: local_gates passed, aws_deployment_verified false. Cost/resources: $0 mock / none.
"""

import asyncio
import json

from common.config import ROOT
from common.deployment_apps import compare_local
from common.gateway_booking import gateway_probe
from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.production_copilot import copilot
from common.support_evaluation import evaluate_support


async def readiness(settings):
    quality = await evaluate_support(settings)
    if quality.overall_score != 1:
        raise ValueError("Release blocked: policy evaluation failed")
    hosts = await compare_local(settings)
    # Synchronous MCP sessions own their event loop in a worker thread.
    policy = await asyncio.to_thread(gateway_probe, settings)
    integration = await asyncio.to_thread(copilot, settings)
    return {
        "local_gates": "passed",
        "quality_score": quality.overall_score,
        "hosting": hosts,
        "policy": policy,
        "integration_tools": integration["tools"],
        "aws_deployment_verified": False,
        "container_build_verified": False,
        "remaining": [
            "Build and scan images",
            "Review synthesized IAM and regional prices",
            "Explicit learner deployment",
            "Live auth, denial, trace and teardown checks",
        ],
    }


def main():
    args, cfg = lesson_settings()
    if not args.mock:
        raise ValueError(
            "This checkpoint is a local gate; use --mock and the separate live lab guides"
        )
    report = asyncio.run(readiness(cfg))
    path = ROOT / ".nimbus/production_readiness.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    complete()


if __name__ == "__main__":
    run_cli(main)
