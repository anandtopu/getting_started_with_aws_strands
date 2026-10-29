"""Bounded Pricing MCP question; the offline rates are illustrative, never live quotes."""

from decimal import Decimal

from strands import Agent, tool

from common.models import get_model
from common.testing import tool_message


def lambda_cost_question(settings, *, client=None):
    @tool
    def lambda_pricing_evidence() -> dict:
        """Read bounded Lambda pricing evidence for the host-selected workload and region."""
        if client is not None:
            # Limit product, page size and response length below model-generated arguments.
            return client.call_tool_sync(
                "lambda-prices",
                "get_pricing",
                {
                    "service_code": "AWSLambda",
                    "region": settings.aws_region,
                    "max_results": 10,
                    "max_allowed_characters": 10000,
                },
            )
        requests = Decimal(1000000)
        gb_seconds = requests * Decimal("0.2") * Decimal("0.5")
        estimate = requests * Decimal("0.0000002") + gb_seconds * Decimal("0.0000166667")
        return {
            "mode": "illustrative fixture, not a live Pricing MCP response",
            "product": "Lambda Event Functions",
            "region": settings.aws_region,
            "requests": int(requests),
            "gb_seconds": str(gb_seconds),
            "request_rate_usd": "0.0000002",
            "gb_second_rate_usd": "0.0000166667",
            "estimated_usd": str(estimate.quantize(Decimal("0.01"))),
            "exclusions": "free tier, model inference, logs, transfer, API Gateway and tax",
        }

    agent = Agent(
        model=get_model(
            settings,
            responses=[
                tool_message("lambda_pricing_evidence", {}),
                "Illustrative Event Functions estimate: $1.87 before free tier and extras. "
                "A live quote requires current matching product, architecture, units and tiers.",
            ],
        ),
        tools=[lambda_pricing_evidence],
        callback_handler=None,
        retry_strategy=None,
        system_prompt=(
            "Use lambda_pricing_evidence once. Explain the unit calculation and exclusions. "
            "The workload is one million requests, 512 MB and 200 ms each. "
            "Never label fixture rates as live. Live evidence is only a bounded first page; "
            "if matching rates or pagination are unresolved, abstain from a price quote and "
            "state which filters/pages are needed. Model inference is a separate cost."
        ),
    )
    return agent(
        "What would running this agent on Lambda cost for that workload?", limits={"turns": 3}
    )
