"""Cross-layer checks for approval authorization, isolation and stream cleanup."""

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from strands import Agent

from common.approvals import ApprovalLedger, approval_agent, request_prompt, responses_for
from common.audit import AuditPolicy, quote_tool, redact
from common.config import load_settings
from common.models import get_model
from common.safety import apply_grounding, injection_trial
from common.streaming import public_stream, sse
from common.testing import tool_message


@pytest.mark.parametrize("decision,expected", [("approve", "applied"), ("reject", "rejected")])
def test_real_interrupt_and_replay(tmp_path, decision, expected):
    ledger = ApprovalLedger(tmp_path / "a.db")
    key = ledger.propose("CUS-001", "DEMO-001", "refund", 60000)
    agent = approval_agent(load_settings(provider="mock"), ledger, key)
    paused = agent(request_prompt(ledger, key))
    assert paused.stop_reason == "interrupt"
    assert ledger.get(key, "CUS-001")["status"] == "pending"
    ledger.decide(key, "CUS-001", decision, supervisor="SUPERVISOR-DEMO")
    agent(responses_for(paused))
    assert ledger.get(key, "CUS-001")["status"] == expected
    if decision == "approve":
        assert ledger.apply(key, "CUS-001")["status"] == "already_applied"
        with ledger.transaction() as db:
            assert (
                db.execute("SELECT refunded FROM bookings WHERE id='DEMO-001'").fetchone()[0]
                == 60000
            )


def test_interrupt_response_alone_is_not_authorization(tmp_path):
    ledger = ApprovalLedger(tmp_path / "a.db")
    key = ledger.propose("CUS-001", "DEMO-001", "refund", 60000)
    agent = approval_agent(load_settings(provider="mock"), ledger, key)
    paused = agent(request_prompt(ledger, key))
    agent([{"interruptResponse": {"interruptId": paused.interrupts[0].id, "response": "approve"}}])
    assert ledger.get(key, "CUS-001")["status"] == "pending"
    with ledger.transaction() as db:
        assert db.execute("SELECT refunded FROM bookings WHERE id='DEMO-001'").fetchone()[0] == 0


def test_model_cannot_replace_the_application_bound_request(tmp_path):
    ledger = ApprovalLedger(tmp_path / "a.db")
    key = ledger.propose("CUS-001", "DEMO-001", "refund", 100)
    other = ledger.propose("CUS-001", "DEMO-001", "refund", 200)
    agent = approval_agent(load_settings(provider="mock"), ledger, key)
    agent.model = get_model(
        provider="mock",
        responses=[tool_message("apply_action", {"request_id": other}), "Rejected."],
    )
    agent("Apply the request")
    assert ledger.get(key, "CUS-001")["status"] == "approved"
    assert ledger.get(other, "CUS-001")["status"] == "approved"
    assert "not bound" in str(agent.messages)


def test_owner_expiry_and_changed_balance(tmp_path):
    ledger = ApprovalLedger(tmp_path / "a.db")
    with pytest.raises(PermissionError):
        ledger.propose("CUS-002", "DEMO-001", "refund", 100)
    key = ledger.propose("CUS-001", "DEMO-001", "change", 0, now=0, ttl=10)
    with pytest.raises(PermissionError):
        ledger.decide(key, "CUS-001", "approve", supervisor="CUSTOMER")
    assert (
        ledger.decide(key, "CUS-001", "approve", supervisor="SUPERVISOR-DEMO", now=10) == "expired"
    )
    with pytest.raises(PermissionError):
        ledger.apply(key, "CUS-001", now=10)
    keys = [ledger.propose("CUS-001", "DEMO-001", "refund", 60000) for _ in range(2)]
    for key in keys:
        ledger.decide(key, "CUS-001", "approve", supervisor="SUPERVISOR-DEMO")
    ledger.apply(keys[0], "CUS-001")
    with pytest.raises(ValueError):
        ledger.apply(keys[1], "CUS-001")


def test_atomic_duplicate_apply(tmp_path):
    ledger = ApprovalLedger(tmp_path / "a.db")
    key = ledger.propose("CUS-001", "DEMO-001", "refund", 50000)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: ledger.apply(key, "CUS-001"), range(2)))
    assert {r["status"] for r in results} == {"applied", "already_applied"}


def test_hooks_redact_budget_and_lifecycle():
    audit = AuditPolicy()
    model = get_model(
        provider="mock", responses=[tool_message("quote_trip", {"destination": " lax "}), "Denied"]
    )
    agent = Agent(model=model, tools=[quote_tool()], hooks=[audit], callback_handler=None)
    agent("Email me at name@example.com", invocation_state=dict(budget_cents=50000))
    assert "name@example.com" not in json.dumps(model.requests)
    assert any(r.get("blocked") for r in audit.rows)
    assert {
        "BeforeModelCallEvent",
        "AfterModelCallEvent",
        "BeforeToolsEvent",
        "AfterToolsEvent",
    } <= set(audit.events)
    assert redact({"text": ["555-123-4567", "hello"]}) == {"text": ["[PHONE]", "hello"]}


def test_attack_boundary_and_grounding_contract():
    cfg = load_settings(provider="mock")
    assert injection_trial(cfg, hardened=False)["tool_executed"]
    assert not injection_trial(cfg, hardened=True)["tool_executed"]
    assert apply_grounding(mock=True)["action"] == "GUARDRAIL_INTERVENED"


@pytest.mark.asyncio
async def test_stream_disconnect_timeout_and_cancellation_close_iterator():
    class Stream:
        closed = False

        async def stream_async(self, *args, **kwargs):
            try:
                yield {"data": "hello\nevent: forged"}
                await asyncio.sleep(30)
            finally:
                self.closed = True

    async def disconnected():
        return True

    stream = Stream()
    assert [x async for x in public_stream(stream, "x", disconnected=disconnected)] == []
    assert stream.closed
    stream = Stream()
    frames = [x async for x in public_stream(stream, "x", seconds=0.02)]
    assert "event: error" in frames[-1] and stream.closed
    assert "\nevent: forged" not in sse("text", {"text": "hello\nevent: forged"})
    stream = Stream()

    async def consume():
        return [x async for x in public_stream(stream, "x")]

    task = asyncio.create_task(consume())
    await asyncio.sleep(0.02)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert stream.closed


def test_sync_stream_consumer_close_cancels_owned_task():
    import threading

    from common.streaming import sync_chunks

    closed = threading.Event()

    async def slow():
        try:
            yield "first"
            await asyncio.sleep(30)
        finally:
            closed.set()

    chunks = sync_chunks(slow())
    assert next(chunks) == "first"
    chunks.close()
    assert closed.wait(timeout=1)


def test_authenticated_web_decision_and_replay(tmp_path):
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from common.web_apps import create_app

    ledger = ApprovalLedger(tmp_path / "a.db")
    with TestClient(
        create_app(
            load_settings(provider="mock"),
            customer_token="customer",
            supervisor_token="supervisor",
            ledger=ledger,
        )
    ) as client:
        owner = {"Authorization": "Bearer customer"}
        supervisor = {"Authorization": "Bearer supervisor"}
        assert client.post("/requests", json={}).status_code == 401
        key = client.post("/requests", json={"cents": 60000}, headers=owner).json()["request"]["id"]
        path = f"/requests/{key}/decision"
        assert client.post(path, json={"decision": "approve"}, headers=owner).status_code == 401
        result = client.post(path, json={"decision": "approve"}, headers=supervisor)
        assert result.status_code == 200 and "event: done" in result.text
        assert ledger.get(key, "CUS-001")["status"] == "applied"
        assert (
            client.post(path, json={"decision": "approve"}, headers=supervisor).status_code == 409
        )
