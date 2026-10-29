"""Local teaching web apps; random bearer tokens stand in for production sign-in."""

import asyncio
import secrets

from common.approvals import approval_agent, request_prompt, responses_for
from common.streaming import planner, public_stream


def create_app(settings, *, customer_token, supervisor_token, ledger=None, tools=()):
    from fastapi import FastAPI, Header, HTTPException, Request
    from fastapi.responses import HTMLResponse, StreamingResponse
    from pydantic import BaseModel, Field

    app = FastAPI(title="Nimbus local learning app")
    pending = {}

    def authorize(header, token):
        if not header or not secrets.compare_digest(header, "Bearer " + token):
            raise HTTPException(401, "A valid local demo token is required")

    class Chat(BaseModel):
        prompt: str = Field(min_length=1, max_length=2000)

    class Proposal(BaseModel):
        booking: str = Field(default="DEMO-001", max_length=32)
        action: str = "refund"
        cents: int = Field(default=60000, strict=True, ge=0, le=100000)

    class Decision(BaseModel):
        decision: str

    @app.get("/", response_class=HTMLResponse)
    def home():
        from common.config import ROOT

        page = (ROOT / "common/web_ui.html").read_text(encoding="utf-8")
        if ledger is None:
            page = page.replace('<section id="booking">', '<section id="booking" hidden>')
            page = page.replace(
                "Plan a trip or review a synthetic booking request.", "Plan a trip."
            )
        return page

    @app.post("/chat")
    async def chat(body: Chat, request: Request, authorization: str | None = Header(None)):
        authorize(authorization, customer_token)
        return StreamingResponse(
            public_stream(planner(settings), body.prompt, disconnected=request.is_disconnected),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-store"},
        )

    @app.post("/requests")
    async def start(body: Proposal, authorization: str | None = Header(None)):
        authorize(authorization, customer_token)
        if ledger is None:
            raise HTTPException(404, "This lesson only enables trip planning")
        if len(pending) >= 32:
            raise HTTPException(429, "Too many pending reviews; finish them or restart the demo")
        try:
            key = ledger.propose("CUS-001", body.booking, body.action, body.cents)
            from common.audit import AuditPolicy

            policy = AuditPolicy(
                allowed=["apply_action", *[t.tool_name for t in tools]], max_tools=4
            )
            agent = approval_agent(settings, ledger, key, hooks=[policy], tools=tools)
            async with asyncio.timeout(30):
                result = await agent.invoke_async(request_prompt(ledger, key), limits={"turns": 4})
            if result.stop_reason == "interrupt":
                pending[key] = (agent, result)
            return {"request": ledger.get(key, "CUS-001"), "stop_reason": result.stop_reason}
        except (ValueError, PermissionError) as exc:
            raise HTTPException(400, str(exc)) from exc
        except TimeoutError as exc:
            raise HTTPException(504, "Proposal timed out; inspect its recorded status") from exc

    @app.post("/requests/{key}/decision")
    async def decide(
        key: str, body: Decision, request: Request, authorization: str | None = Header(None)
    ):
        authorize(authorization, supervisor_token)
        if ledger is None or key not in pending:
            raise HTTPException(409, "No paused request exists in this server process")
        try:
            ledger.decide(key, "CUS-001", body.decision, supervisor="SUPERVISOR-DEMO")
        except (ValueError, PermissionError) as exc:
            raise HTTPException(409, str(exc)) from exc
        agent, result = pending.pop(key)
        return StreamingResponse(
            public_stream(agent, responses_for(result), disconnected=request.is_disconnected),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-store"},
        )

    @app.get("/requests/{key}")
    def status(key: str, authorization: str | None = Header(None)):
        authorize(authorization, customer_token)
        if ledger is None:
            raise HTTPException(404)
        try:
            return ledger.get(key, "CUS-001")
        except PermissionError as exc:
            raise HTTPException(404, "Unknown customer request") from exc

    return app


def demonstrate(settings, *, ledger=None):
    """Exercise the ASGI routes without starting a long-lived web server."""
    from fastapi.testclient import TestClient

    app = create_app(
        settings,
        customer_token="offline-customer",
        supervisor_token="offline-supervisor",
        ledger=ledger,
    )
    with TestClient(app) as client:
        customer = {"Authorization": "Bearer offline-customer"}
        response = client.post("/chat", json={"prompt": "Plan a Boston trip"}, headers=customer)
        assert response.status_code == 200 and "event: done" in response.text
        if ledger:
            proposed = client.post("/requests", json={"cents": 60000}, headers=customer)
            assert proposed.status_code == 200, proposed.text
            key = proposed.json()["request"]["id"]
            response = client.post(
                f"/requests/{key}/decision",
                json={"decision": "reject"},
                headers={"Authorization": "Bearer offline-supervisor"},
            )
            assert (
                response.status_code == 200 and ledger.get(key, "CUS-001")["status"] == "rejected"
            )
    print("SSE and authenticated routes verified")


def serve(settings, *, ledger=None, port=8765, tools=()):
    import uvicorn

    customer, supervisor = secrets.token_urlsafe(24), secrets.token_urlsafe(24)
    print(f"Open http://127.0.0.1:{port} — local demo only")
    print(f"Customer token: {customer}\nSupervisor token: {supervisor}")
    uvicorn.run(
        create_app(
            settings,
            customer_token=customer,
            supervisor_token=supervisor,
            ledger=ledger,
            tools=tools,
        ),
        host="127.0.0.1",
        port=port,
        log_level="warning",
        access_log=False,
    )
