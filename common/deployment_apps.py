"""Validated hosting adapters around the same stateless Nimbus support implementation."""

import json
import os
import secrets
from typing import Any

from common.config import Settings, load_settings
from common.production_support import answer_support, stream_support


def runtime_app(settings: Settings | None = None):
    from bedrock_agentcore.runtime import BedrockAgentCoreApp

    app = BedrockAgentCoreApp()

    @app.entrypoint
    async def invoke(payload, context):
        if isinstance(payload, dict) and payload.get("operation") == "copilot":
            import asyncio

            from common.flagship_runtime import hosted_copilot

            # The credential stays in trusted transport code, outside agent messages and outputs.
            result = await asyncio.to_thread(hosted_copilot, payload, settings or load_settings())
            yield {"type": "done", "result": result}
            return
        # Runtime session isolation is hosting isolation; this lesson creates fresh agent state.
        async for event in stream_support(payload, settings or load_settings()):
            yield event

    return app


def fargate_app(settings: Settings | None = None, *, token: str | None = None):
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import StreamingResponse
    from pydantic import ValidationError

    from common.production_support import SupportRequest

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/invocations")
    async def invoke(request: Request):
        expected = token or os.environ.get("NIMBUS_API_TOKEN")
        if not expected or not secrets.compare_digest(
            request.headers.get("authorization", ""), "Bearer " + expected
        ):
            raise HTTPException(401, "Authentication required")
        # Bound body accumulation even when Content-Length is missing or forged.
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 8192:
                raise HTTPException(413, "Request too large")
        try:
            payload = SupportRequest.model_validate_json(body).model_dump()
        except (ValidationError, ValueError):
            raise HTTPException(422, "Supply only a prompt of 1 to 2000 characters") from None

        async def frames():
            try:
                async for event in stream_support(payload, settings or load_settings()):
                    if await request.is_disconnected():
                        return
                    yield "data: " + json.dumps(event) + "\n\n"
            except Exception:
                yield (
                    "event: error\ndata: "
                    '{"message":"Request failed; retry after checking status"}\n\n'
                )

        return StreamingResponse(
            frames(), media_type="text/event-stream", headers={"Cache-Control": "no-store"}
        )

    return app


async def compare_local(settings: Settings) -> dict[str, Any]:
    """HTTP-contract checks, not simulated AWS latency or capacity measurements."""
    import httpx

    payload = {"prompt": "How long does an approved refund take?"}
    direct = await answer_support(payload, settings)
    reports = {"lambda_core": {"usage": direct["usage"], "seconds": direct["seconds"]}}
    for name, app, headers in [
        ("agentcore_http", runtime_app(settings), {}),
        (
            "fargate_http",
            fargate_app(settings, token="local-contract-token"),
            {"Authorization": "Bearer local-contract-token"},
        ),
    ]:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://localhost"
        ) as client:
            response = await client.post("/invocations", json=payload, headers=headers)
            response.raise_for_status()
            if "5 to 10" not in response.text:
                raise AssertionError("Hosted contract lost the policy response")
            reports[name] = {"status": response.status_code, "streamed": "done" in response.text}
    reports["scope"] = "Local handlers/ASGI only; no AWS hosting measurements"
    return reports


def serve():
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["runtime", "fargate"])
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    cfg = load_settings(provider="mock" if args.mock else None)
    if args.kind == "fargate" and not os.environ.get("NIMBUS_API_TOKEN"):
        raise ValueError("Set NIMBUS_API_TOKEN through the environment or ECS secret injection")
    app = runtime_app(cfg) if args.kind == "runtime" else fargate_app(cfg)
    uvicorn.run(app, host=args.host, port=args.port, access_log=False)


if __name__ == "__main__":
    serve()
