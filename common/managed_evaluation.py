"""Evaluate explicitly reviewed session spans; metadata-only traces cannot be semantic evidence."""

import json
import math
from contextlib import nullcontext
from pathlib import Path

from botocore.stub import Stubber

from common.cloud_clients import client


def evaluate_spans(settings, path: Path | None = None):
    if settings.provider == "mock":
        # A service-contract fixture, deliberately NOT described as a judge quality test.
        spans = [{"traceId": "1" * 32, "spanId": "2" * 16, "name": "synthetic"}]
    else:
        if not path or path.stat().st_size > 256_000:
            raise ValueError("Supply a reviewed session-spans JSON file smaller than 256 KB")
        spans = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(spans, list) or not 1 <= len(spans) <= 100:
        raise ValueError("Supply 1 to 100 reviewed span records for one session")
    api = client("bedrock-agentcore", settings)
    request = {"evaluatorId": "Builtin.Helpfulness", "evaluationInput": {"sessionSpans": spans}}
    stub = Stubber(api)
    if settings.provider == "mock":
        stub.add_response(
            "evaluate",
            {
                "evaluationResults": [
                    {
                        "evaluatorId": "Builtin.Helpfulness",
                        "evaluatorArn": (
                            "arn:aws:bedrock-agentcore:::evaluator/Builtin.Helpfulness"
                        ),
                        "evaluatorName": "Helpfulness",
                        "context": {"spanContext": {"sessionId": "synthetic"}},
                        "value": 1.0,
                        "explanation": "Scripted contract rating",
                    }
                ]
            },
            request,
        )
    with stub if settings.provider == "mock" else nullcontext():
        results = api.evaluate(**request)["evaluationResults"]
        if settings.provider == "mock":
            stub.assert_no_pending_responses()
    # Partial failures and empty responses must not disappear in an average.
    if not results or any(row.get("errorCode") or "value" not in row for row in results):
        raise ValueError("Managed evaluation returned incomplete results")
    scores = [row["value"] for row in results]
    if any(
        type(score) not in (int, float) or not math.isfinite(score) or not 0 <= score <= 1
        for score in scores
    ):
        raise ValueError("Managed evaluation returned an invalid normalized score")
    return {
        "scores": scores,
        "scope": "Stubber contract" if settings.provider == "mock" else "Managed judge",
    }
