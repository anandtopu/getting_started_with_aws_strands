"""Production boundaries are checked without credentials or external services."""

import asyncio
import importlib.util
import json
from types import SimpleNamespace

import pytest

from common.config import ROOT, load_settings
from common.production_support import answer_support, lambda_handler, search_policies
from common.public_booking import refund_quote


@pytest.fixture
def cfg():
    return load_settings(provider="mock")


async def test_support_has_evidence_and_measured_tool_usage(cfg):
    result = await answer_support({"prompt": "How long does a refund take?"}, cfg)
    assert "5 to 10" in result["answer"]
    assert result["tools"] == ["search_policies"]
    assert result["usage"]["totalTokens"] == 240
    assert result["tool_metrics"]["search_policies"]["success_count"] == 1


def test_lambda_and_tool_work_without_server(cfg):
    assert (
        "policies/refund.md"
        in lambda_handler({"prompt": "Refund time?"}, None, settings=cfg)["answer"]
    )
    assert search_policies("Refund time?")
    with pytest.raises(ValueError):
        search_policies("x" * 2001)


@pytest.mark.parametrize(
    "payload", [{}, {"prompt": ""}, {"prompt": "x", "token": "secret"}, {"prompt": 5}]
)
async def test_support_rejects_invalid_payload(cfg, payload):
    with pytest.raises(ValueError):
        await answer_support(payload, cfg)


async def test_real_evals_detect_regression(cfg):
    pytest.importorskip("strands_evals")
    from common.support_evaluation import evaluate_support, judge_demo

    good = await evaluate_support(cfg)
    bad = await evaluate_support(cfg, regression=True)
    assert good.overall_score == 1.0
    assert bad.overall_score == 0.5
    assert all(row["test_pass"] for row in await judge_demo(cfg))


def test_actual_cli_preserves_quality_failure():
    pytest.importorskip("strands_evals")
    from common.evaluation_cli import gate

    assert gate()["exit_code"] == 0
    assert gate(regression=True, fail_on="threshold:0.9")["exit_code"] == 1


async def test_http_auth_body_limits_and_stream(cfg):
    pytest.importorskip("fastapi")
    import httpx

    from common.deployment_apps import fargate_app

    app = fargate_app(cfg, token="local-test-token")
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://localhost"
    ) as client:
        assert (await client.get("/health")).status_code == 200
        assert (await client.post("/invocations", json={"prompt": "refund"})).status_code == 401
        headers = {"Authorization": "Bearer local-test-token"}
        assert (
            await client.post("/invocations", content=b"x" * 8193, headers=headers)
        ).status_code == 413
        assert (
            await client.post("/invocations", json={"prompt": "x", "extra": 1}, headers=headers)
        ).status_code == 422
        responses = await asyncio.gather(
            *[
                client.post("/invocations", json={"prompt": "Refund time?"}, headers=headers)
                for _ in range(2)
            ]
        )
        for response in responses:
            assert response.status_code == 200
            events = [
                json.loads(line[6:])
                for line in response.text.splitlines()
                if line.startswith("data: ")
            ]
            assert events[-1]["type"] == "done"
            assert events[-1]["usage"]["totalTokens"] == 240
            assert "local-test-token" not in response.text


async def test_agentcore_actual_entrypoint(cfg):
    pytest.importorskip("bedrock_agentcore")
    pytest.importorskip("fastapi")
    from common.deployment_apps import compare_local

    report = await compare_local(cfg)
    assert report["agentcore_http"]["streamed"]


def test_hosting_api_contracts(cfg):
    from common.deployment_calls import invoke_lambda, invoke_runtime, runtime_configuration

    assert invoke_lambda(cfg, "nimbus-support")["response"]["tools"] == ["search_policies"]
    assert (
        len(
            invoke_runtime(
                cfg, "arn:aws:bedrock-agentcore:us-east-1:111122223333:runtime/nimbus-AbCdEf1234"
            )["session_id"]
        )
        == 36
    )
    config = runtime_configuration(cfg, "/nimbus/service", "nimbus-token")
    assert config == {"service_name": "nimbus-support", "credential_loaded": True}


def test_memory_and_managed_eval_contracts(cfg):
    from common.agentcore_memory import preferences
    from common.managed_evaluation import evaluate_spans

    assert preferences(cfg, "NimbusDemo-1234567890", "CUS-001")["event_deleted"]
    with pytest.raises(ValueError):
        preferences(cfg, "NimbusDemo-1234567890", "../other-customer")
    assert evaluate_spans(cfg)["scores"] == [1.0]


def test_built_in_sessions_stop(cfg):
    pytest.importorskip("bedrock_agentcore")
    from common.agentcore_tools import calculate_receipts, read_receipt_page

    assert calculate_receipts(cfg)["output"] == "29800"
    assert read_receipt_page(cfg)["stopped"]


def test_interpreter_stops_after_execution_failure(monkeypatch, cfg):
    module = pytest.importorskip("bedrock_agentcore.tools.code_interpreter_client")
    from common.agentcore_tools import calculate_receipts
    from common.cloud_clients import client

    stopped = []

    class BrokenInterpreter:
        def __init__(self, *args, **kwargs):
            self.data_plane_client = client("bedrock-agentcore", cfg)

        def start(self, **kwargs):
            return "session"

        def invoke(self, *args):
            raise RuntimeError("injected tool failure")

        def stop(self):
            stopped.append(True)

    monkeypatch.setattr(module, "CodeInterpreter", BrokenInterpreter)
    monkeypatch.setattr("common.agentcore_tools.session", lambda _: None)
    with pytest.raises(RuntimeError, match="injected"):
        calculate_receipts(cfg.model_copy(update={"provider": "bedrock"}))
    assert stopped == [True]


@pytest.mark.parametrize("amount", [0, -1, 50001, True, 500.0, "500"])
def test_refund_invalid_amounts(amount):
    with pytest.raises(ValueError):
        refund_quote(amount)


def test_refund_inclusive_limit():
    assert refund_quote(50000) == {"amount_cents": 50000, "within_limit": True, "quote_only": True}


@pytest.mark.local_protocol
def test_gateway_policy_boundary(cfg):
    from common.gateway_booking import gateway_probe

    result = gateway_probe(cfg)
    assert result["within_limit"] == "success"
    assert result["over_limit"] == "error"


def test_gateway_rejects_untrusted_destination_before_credentials(cfg):
    from common.gateway_booking import gateway_client

    for url in (
        "http://evil.example/mcp",
        "https://evil.example/mcp",
        "https://abc.gateway.bedrock-agentcore.us-east-1.amazonaws.com.evil.example/mcp",
    ):
        with pytest.raises(ValueError):
            gateway_client(cfg.model_copy(update={"provider": "bedrock"}), url=url, token="private")


def test_identity_checks_signature_scope_expiry_and_client():
    jwt = pytest.importorskip("jwt")
    import time

    from cryptography.hazmat.primitives.asymmetric import rsa

    from common.agentcore_identity import verify_token

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    payload = {
        "iss": "https://nimbus.example",
        "sub": "traveler-a",
        "iat": int(time.time()),
        "exp": int(time.time()) + 60,
        "client_id": "client",
        "token_use": "access",
        "scope": "nimbus/read",
    }

    def verify(data, signing_key=key):
        return verify_token(
            jwt.encode(data, signing_key, algorithm="RS256"),
            key.public_key(),
            issuer=payload["iss"],
            client_id="client",
        )

    assert verify(payload)["actor"] == "traveler-a"
    for changes in (
        {"exp": 1},
        {"iss": "https://evil.example"},
        {"scope": "other"},
        {"client_id": "other"},
        {"token_use": "id"},
    ):
        with pytest.raises((ValueError, jwt.PyJWTError)):
            verify({**payload, **changes})
    with pytest.raises(jwt.InvalidSignatureError):
        verify(payload, rsa.generate_private_key(public_exponent=65537, key_size=2048))


def test_packaging_excludes_working_tree_and_secrets():
    from scripts.prepare_deployment import prepare

    for kind in ("lambda", "runtime", "fargate"):
        path = prepare(kind)
        assert not (path / ".env").exists()
        assert not (path / ".aws").exists()
        assert not (path / "data/bookings.db").exists()
        assert (path / "common/production_support.py").read_bytes() == (
            ROOT / "common/production_support.py"
        ).read_bytes()
        assert "--require-hashes" in (path / "Dockerfile").read_text()
        assert "AWS_PROFILE" not in (path / "Dockerfile").read_text()
        assert (path / "common/scheduled_evaluation.py").is_file()


def test_pkce_and_callback_boundary():
    from urllib.parse import parse_qs, urlsplit

    from scripts.cognito_copilot import authorization_request, callback_code

    url = authorization_request(
        "https://nimbus.auth.us-east-1.amazoncognito.com",
        "us-east-1",
        "client",
        "one-use-state",
        "x" * 64,
    )
    params = parse_qs(urlsplit(url).query)
    assert params["code_challenge_method"] == ["S256"]
    assert params["redirect_uri"] == ["http://localhost:8765/callback"]
    assert "x" * 64 not in url
    assert callback_code("/callback?state=one-use-state&code=example", "one-use-state") == "example"
    for path in (
        "/callback?state=wrong&code=example",
        "/other?state=one-use-state&code=x",
        "/callback?state=one-use-state&error=denied",
    ):
        with pytest.raises(ValueError):
            callback_code(path, "one-use-state")
    with pytest.raises(ValueError):
        authorization_request("https://attacker.example", "us-east-1", "client", "state", "v")


def test_openapi_target_is_scoped_and_shape_validated(cfg):
    from common.gateway_openapi import openapi_target

    request = openapi_target(
        cfg, "nimbus-booking-abcdefghij", "https://abc123.execute-api.us-east-1.amazonaws.com/demo"
    )
    schema = json.loads(request["targetConfiguration"]["mcp"]["openApiSchema"]["inlinePayload"])
    assert schema["paths"]["/flights"]["get"]["operationId"] == "searchFlights"
    assert (
        request["credentialProviderConfigurations"][0]["credentialProvider"][
            "iamCredentialProvider"
        ]["service"]
        == "execute-api"
    )
    with pytest.raises(ValueError):
        openapi_target(cfg, "nimbus-booking-abcdefghij", "https://untrusted.example/demo")


def test_aws_otlp_signing_and_http_failure(cfg):
    pytest.importorskip("opentelemetry.exporter.otlp.proto.http")
    import httpx
    from opentelemetry.sdk.trace.export import SpanExportResult

    from common.aws_otlp import AWSOTLPExporter

    seen = []

    def receive(request):
        seen.append(request)
        return httpx.Response(403)

    exporter = AWSOTLPExporter(cfg, transport=httpx.MockTransport(receive))
    try:
        assert exporter.export([]) == SpanExportResult.FAILURE
    finally:
        exporter.shutdown()
    assert seen[0].url.host == "xray.us-east-1.amazonaws.com"
    assert seen[0].headers["authorization"].startswith("AWS4-HMAC-SHA256 ")
    assert seen[0].headers["content-type"] == "application/x-protobuf"


def test_scheduled_job_fails_closed_and_closes_body(monkeypatch):
    import io

    import boto3

    spec = importlib.util.spec_from_file_location(
        "scheduled_judge", ROOT / "common/scheduled_evaluation.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setenv("TRACE_BUCKET", "synthetic")
    bodies = []

    def get_object(**kwargs):
        stream = io.BytesIO(b'[{"name":"synthetic"}]')
        bodies.append(stream)
        return {"Body": stream}

    for results in (
        [],
        [{"errorCode": "failed"}],
        [{"value": 0.7}],
        *[[{"value": value}] for value in (float("nan"), float("inf"), True, "1", -1, 2)],
    ):
        monkeypatch.setattr(
            boto3,
            "client",
            lambda service, results=results: (
                SimpleNamespace(get_object=get_object)
                if service == "s3"
                else SimpleNamespace(evaluate=lambda **kw: {"evaluationResults": results})
            ),
        )
        with pytest.raises(ValueError):
            module.handler({}, None)
        assert bodies[-1].closed


def test_aws_otlp_rejected_and_malformed_success_responses(cfg):
    pytest.importorskip("opentelemetry.exporter.otlp.proto.http")
    import httpx
    from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceResponse
    from opentelemetry.sdk.trace.export import SpanExportResult

    from common.aws_otlp import AWSOTLPExporter

    rejected = ExportTraceServiceResponse()
    rejected.partial_success.rejected_spans = 1
    for payload, expected in (
        (rejected.SerializeToString(), SpanExportResult.FAILURE),
        (b"malformed-response", SpanExportResult.FAILURE),
        (b"", SpanExportResult.SUCCESS),
    ):
        exporter = AWSOTLPExporter(
            cfg,
            transport=httpx.MockTransport(
                lambda request, payload=payload: httpx.Response(200, content=payload)
            ),
        )
        try:
            assert exporter.export([]) == expected
        finally:
            exporter.shutdown()


@pytest.mark.live
async def test_live_support_policy_evidence():
    result = await answer_support({"prompt": "How long does a refund take?"}, load_settings())
    assert "5" in result["answer"] and "10" in result["answer"]
