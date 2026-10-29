"""Bounded built-in service sessions; no model-generated code, arbitrary URLs or credentials."""

import json
from contextlib import nullcontext
from datetime import UTC, datetime

from botocore.stub import Stubber

from common.cloud_clients import client, session

CODE = "print(sum([7500, 12500, 9800]))"


def builtin_agent(settings, kind):
    from strands import tool

    from common.coordination import worker
    from common.testing import tool_message

    operation = {"code": calculate_receipts, "browser": read_receipt_page}[kind]
    results = []
    attempted = []

    @tool
    def reviewed_service() -> dict:
        """Read the host's synthetic receipt using one bounded managed session."""
        if attempted:
            raise ValueError("The managed service has already been called")
        attempted.append(True)
        result = operation(settings)
        results.append(result)
        return result

    agent = worker(
        settings,
        "receipt_reader",
        [tool_message("reviewed_service", {}), "The synthetic receipt total is USD 298.00."],
        tools=[reviewed_service],
        prompt="Call reviewed_service once and report its synthetic receipt total. "
        "Do not execute other code.",
    )
    result = agent("Read the reviewed receipt.", limits={"turns": 2})
    if not results or not results[0]["stopped"]:
        raise ValueError("Managed session did not return a checked result")
    return {
        "answer": str(result),
        "service": results[0],
        "usage": dict(result.metrics.accumulated_usage),
    }


def calculate_receipts(settings):
    from bedrock_agentcore.tools.code_interpreter_client import CodeInterpreter

    interpreter = CodeInterpreter(settings.aws_region, session=session(settings))
    stub = Stubber(interpreter.data_plane_client)
    identifier, session_id = "aws.codeinterpreter.v1", "a" * 36
    common = {"codeInterpreterIdentifier": identifier, "sessionId": session_id}
    now = datetime.now(UTC)
    if settings.provider == "mock":
        stub.add_response(
            "start_code_interpreter_session",
            {**common, "createdAt": now},
            {
                "codeInterpreterIdentifier": identifier,
                "name": "nimbus-receipts",
                "sessionTimeoutSeconds": 60,
            },
        )
        stub.add_response(
            "invoke_code_interpreter",
            {
                "stream": {
                    "result": {"content": [{"type": "text", "text": "29800"}], "isError": False}
                }
            },
            {**common, "name": "executeCode", "arguments": {"code": CODE, "language": "python"}},
        )
        stub.add_response("stop_code_interpreter_session", {**common, "lastUpdatedAt": now}, common)
    with stub if settings.provider == "mock" else nullcontext():
        interpreter.start(name="nimbus-receipts", session_timeout_seconds=60)
        try:
            response = interpreter.invoke("executeCode", {"code": CODE, "language": "python"})
            # Stubber validates an event-union dictionary; live responses provide an EventStream.
            stream = [response["stream"]] if settings.provider == "mock" else response["stream"]
            texts = []
            for event in stream:
                result = event.get("result")
                if not result or result.get("isError"):
                    raise ValueError("Code Interpreter reported an execution failure")
                texts.extend(row["text"] for row in result.get("content", []) if "text" in row)
        finally:
            interpreter.stop()
        if settings.provider == "mock":
            stub.assert_no_pending_responses()
    return {
        "output": "\n".join(texts),
        "stopped": True,
        "scope": "Stubber contract" if settings.provider == "mock" else "Remote sandbox",
    }


def _read_browser_page(url, credentials, region):
    """Use Chrome DevTools Protocol to read one host-owned synthetic document."""
    from urllib.parse import urlsplit

    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    from websockets.sync.client import connect

    target = urlsplit(url)
    if target.scheme != "wss" or target.hostname != f"bedrock-agentcore.{region}.amazonaws.com":
        raise ValueError("Unexpected browser automation endpoint")
    request = AWSRequest(method="GET", url=url.replace("wss:", "https:", 1))
    SigV4Auth(credentials, "bedrock-agentcore", region).add_auth(request)
    with connect(
        url,
        additional_headers=dict(request.headers),
        open_timeout=5,
        close_timeout=3,
        max_size=65536,
    ) as ws:
        serial = 0

        def call(method, params, session_id=None):
            nonlocal serial
            serial += 1
            message = {"id": serial, "method": method, "params": params}
            if session_id:
                message["sessionId"] = session_id
            ws.send(json.dumps(message))
            for _ in range(100):
                reply = json.loads(ws.recv(timeout=5))
                if reply.get("id") == serial:
                    if "error" in reply:
                        raise ValueError("Browser command failed")
                    return reply["result"]
            raise TimeoutError("Browser did not acknowledge the command")

        target_id = call("Target.createTarget", {"url": "about:blank"})["targetId"]
        attached = call("Target.attachToTarget", {"targetId": target_id, "flatten": True})[
            "sessionId"
        ]
        # Fixed document, no remote browsing or navigation controlled by an LLM.
        call("Page.enable", {}, attached)
        frame = call("Page.getFrameTree", {}, attached)["frameTree"]["frame"]["id"]
        call(
            "Page.setDocumentContent",
            {
                "frameId": frame,
                "html": "<title>Nimbus receipt</title><p>Receipt total: USD 298.00</p>",
            },
            attached,
        )
        result = call(
            "Runtime.evaluate",
            {"expression": "document.body.innerText", "returnByValue": True},
            attached,
        )
        return result["result"]["value"]


def read_receipt_page(settings):
    api = client("bedrock-agentcore", settings)
    identifier, session_id = "aws.browser.v1", "b" * 36
    common = {"browserIdentifier": identifier, "sessionId": session_id}
    now = datetime.now(UTC)
    start = {"browserIdentifier": identifier, "name": "nimbus-receipt", "sessionTimeoutSeconds": 60}
    stub = Stubber(api)
    if settings.provider == "mock":
        stub.add_response("start_browser_session", {**common, "createdAt": now}, start)
        stub.add_response("stop_browser_session", {**common, "lastUpdatedAt": now}, common)
    with stub if settings.provider == "mock" else nullcontext():
        response = api.start_browser_session(**start)
        try:
            if settings.provider == "mock":
                text = "Receipt total: USD 298.00 (fixture; browser engine not executed)"
            else:
                url = response["streams"]["automationStream"]["streamEndpoint"]
                text = _read_browser_page(
                    url,
                    session(settings).get_credentials().get_frozen_credentials(),
                    settings.aws_region,
                )
        finally:
            api.stop_browser_session(
                browserIdentifier=response["browserIdentifier"], sessionId=response["sessionId"]
            )
        if settings.provider == "mock":
            stub.assert_no_pending_responses()
    return {"text": text, "stopped": True}
