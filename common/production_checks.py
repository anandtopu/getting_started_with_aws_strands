"""Small, deterministic tests and content-free CloudWatch metrics."""

from contextlib import nullcontext

from botocore.stub import Stubber

from common.cloud_clients import client


def offline_checks():
    import boto3
    from moto import mock_aws

    from common.production_support import search_policies

    evidence = search_policies("Refund processing time")
    assert any("5 to 10" in row["text"] for row in evidence)
    with mock_aws():
        api = boto3.client(
            "s3",
            region_name="us-east-1",
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
        )
        api.create_bucket(Bucket="nimbus-unit-sessions")
        api.put_object(Bucket="nimbus-unit-sessions", Key="synthetic/session.json", Body=b"{}")
        body = api.get_object(Bucket="nimbus-unit-sessions", Key="synthetic/session.json")["Body"]
        try:
            assert body.read() == b"{}"
        finally:
            body.close()
    return {"tool_test": "passed", "moto_s3_round_trip": "passed", "aws_calls": 0}


def emit_metrics(settings, result):
    api = client("cloudwatch", settings)
    request = {
        "Namespace": "Nimbus/Course",
        "MetricData": [
            {"MetricName": "Tokens", "Value": result["usage"]["totalTokens"], "Unit": "Count"},
            {"MetricName": "Latency", "Value": result["seconds"], "Unit": "Seconds"},
        ],
    }
    stub = Stubber(api)
    if settings.provider == "mock":
        stub.add_response("put_metric_data", {}, request)
    with stub if settings.provider == "mock" else nullcontext():
        api.put_metric_data(**request)
        if settings.provider == "mock":
            stub.assert_no_pending_responses()
    return {"metrics": 2, "content_fields": 0, "namespace": "Nimbus/Course"}
