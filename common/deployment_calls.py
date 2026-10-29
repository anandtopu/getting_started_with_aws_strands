"""AWS hosting/configuration invocations with validated offline service contracts."""

import io
import json
import time
import uuid
from contextlib import nullcontext

from botocore.response import StreamingBody
from botocore.stub import Stubber

from common.cloud_clients import client


def invoke_runtime(settings, arn: str):
    api = client("bedrock-agentcore", settings)
    session_id = str(uuid.uuid4())  # Runtime requires at least 33 characters.
    request = dict(
        agentRuntimeArn=arn,
        runtimeSessionId=session_id,
        payload=json.dumps({"prompt": "Refund processing time?"}).encode(),
        contentType="application/json",
        accept="text/event-stream",
    )
    stub = Stubber(api)
    if settings.provider == "mock":
        body = b'data: {"type":"text","text":"5 to 10 business days"}\n\n'
        stub.add_response(
            "invoke_agent_runtime",
            {
                "response": StreamingBody(io.BytesIO(body), len(body)),
                "contentType": "text/event-stream",
                "statusCode": 200,
            },
            request,
        )
    start = time.monotonic()
    with stub if settings.provider == "mock" else nullcontext():
        response = api.invoke_agent_runtime(**request)
        stream = response["response"]
        try:
            text = stream.read(65537)
            if len(text) > 65536:
                raise ValueError("Runtime response exceeded the lesson's 64 KiB limit")
        finally:
            stream.close()
        if settings.provider == "mock":
            stub.assert_no_pending_responses()
    return {
        "session_id": session_id,
        "content_type": response["contentType"],
        "body": text.decode(),
        "seconds": time.monotonic() - start,
        "scope": "Stubber contract" if settings.provider == "mock" else "Live Runtime",
    }


def invoke_lambda(settings, function_name: str):
    api = client("lambda", settings)
    request = dict(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps({"prompt": "Refund processing time?"}).encode(),
    )
    stub = Stubber(api)
    if settings.provider == "mock":
        body = b'{"answer":"5 to 10 business days","tools":["search_policies"]}'
        stub.add_response(
            "invoke",
            {"StatusCode": 200, "Payload": StreamingBody(io.BytesIO(body), len(body))},
            request,
        )
    start = time.monotonic()
    with stub if settings.provider == "mock" else nullcontext():
        response = api.invoke(**request)
        stream = response["Payload"]
        try:
            payload = stream.read(65537)
        finally:
            stream.close()
        if response.get("FunctionError") or len(payload) > 65536:
            raise ValueError("Lambda failed or returned an oversized response")
        if settings.provider == "mock":
            stub.assert_no_pending_responses()
    return {
        "response": json.loads(payload),
        "seconds": time.monotonic() - start,
        "scope": "Stubber contract" if settings.provider == "mock" else "Live Lambda",
    }


def runtime_configuration(settings, parameter_name: str, secret_id: str):
    ssm, secrets = client("ssm", settings), client("secretsmanager", settings)
    a, b = Stubber(ssm), Stubber(secrets)
    if settings.provider == "mock":
        a.add_response(
            "get_parameter",
            {"Parameter": {"Name": parameter_name, "Type": "String", "Value": "nimbus-support"}},
            {"Name": parameter_name},
        )
        b.add_response(
            "get_secret_value", {"SecretString": "offline-only-demo-value"}, {"SecretId": secret_id}
        )
    with (
        a if settings.provider == "mock" else nullcontext(),
        b if settings.provider == "mock" else nullcontext(),
    ):
        config = ssm.get_parameter(Name=parameter_name)["Parameter"]["Value"]
        secret = secrets.get_secret_value(SecretId=secret_id)["SecretString"]
        if settings.provider == "mock":
            a.assert_no_pending_responses()
            b.assert_no_pending_responses()
    # Secrets are consumed by trusted transport/configuration, never returned in prompts or logs.
    return {"service_name": config, "credential_loaded": bool(secret)}
