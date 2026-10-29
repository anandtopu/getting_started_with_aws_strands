"""Scheduled managed evaluation of one explicitly reviewed synthetic session export."""

import json
import math
import os

import boto3


def handler(event, context):
    body = boto3.client("s3").get_object(
        Bucket=os.environ["TRACE_BUCKET"], Key="session-spans.json"
    )["Body"]
    try:
        raw = body.read(256001)
    finally:
        body.close()
    if len(raw) > 256000:
        raise ValueError("Reviewed session export exceeds 256 KB")
    spans = json.loads(raw)
    if not isinstance(spans, list) or not 1 <= len(spans) <= 100:
        raise ValueError("Supply 1 to 100 reviewed spans for one session")
    results = boto3.client("bedrock-agentcore").evaluate(
        evaluatorId="Builtin.Helpfulness", evaluationInput={"sessionSpans": spans}
    )["evaluationResults"]
    if not results or any(r.get("errorCode") or "value" not in r for r in results):
        raise ValueError("Managed evaluation incomplete")
    # Never log prompts, credentials, retrieved records or judge explanations.
    scores = [r["value"] for r in results]
    if any(
        type(score) not in (int, float) or not math.isfinite(score) or not 0 <= score <= 1
        for score in scores
    ):
        raise ValueError("Managed evaluation returned an invalid normalized score")
    print(json.dumps({"evaluation_scores": scores}))
    if min(scores) < 0.8:
        raise ValueError("Scheduled quality threshold failed")
    return {"scores": scores}
