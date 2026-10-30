"""Actual authenticated HTTP across an owned child-process boundary."""

from types import SimpleNamespace

import httpx
import pytest
from pydantic import ValidationError

from common.config import load_settings
from common.partner_client import (
    UpgradeOffer,
    ask_partner,
    partner_process,
    validated_partner_result,
)


@pytest.mark.local_protocol
@pytest.mark.parametrize("backend", ["strands", "langgraph"])
async def test_partner_card_auth_streaming_interop_and_shutdown(backend):
    pytest.importorskip("a2a")
    if backend == "langgraph":
        pytest.importorskip("langgraph")
    with partner_process(load_settings(provider="mock"), backend=backend) as (url, token):
        async with httpx.AsyncClient(trust_env=False, timeout=10) as client:
            assert (await client.get(url + ".well-known/agent-card.json")).status_code == 401
            assert (await client.post(url, json={})).status_code == 401
            assert (await client.post(url + "_shutdown")).status_code == 401
            card = (
                await client.get(
                    url + ".well-known/agent-card.json",
                    headers={"Authorization": "Bearer " + token},
                )
            ).json()
            assert card["security"] and card["securitySchemes"]
        regular = await ask_partner(url, token)
        streamed = await ask_partner(url, token, streaming=True)
        assert regular["offer"] == streamed["offer"]
        assert regular["protocol_version"] == "0.3.0"
        assert "TaskArtifactUpdateEvent" in streamed["events"]
        assert streamed["offer"]["cents"] == 7500
        assert "not supplied" in streamed["usage"]
        # Four independent contexts exceed one fixture agent's three-request script.
        # A shared Agent/history regression would exhaust that script on the fourth call.
        for _ in range(2):
            assert (await ask_partner(url, token))["offer"] == regular["offer"]
    async with httpx.AsyncClient(trust_env=False, timeout=1) as client:
        with pytest.raises((httpx.ConnectError, httpx.ConnectTimeout)):
            await client.get(url)


def test_remote_quote_contract_rejects_unreviewed_terms():
    quote = dict(
        offer_id="UP-001", flight_id="FLT-0001", cents=7500, currency="USD", quote_only=True
    )
    for bad in (
        {"cents": 1},
        {"quote_only": False},
        {"flight_id": "FLT-0002"},
        {"charge_card": True},
    ):
        with pytest.raises(ValidationError):
            UpgradeOffer.model_validate({**quote, **bad})


def test_streamed_quote_fragments_preserve_identifiers_and_reject_failed_tasks():
    from common.partner_server import upgrade_quote

    expected = UpgradeOffer.model_validate(upgrade_quote())
    result = SimpleNamespace(
        stop_reason="end_turn",
        state={"a2a_task_state": "completed"},
        message={"content": [{"text": char} for char in expected.model_dump_json()]},
    )
    assert validated_partner_result(result) == expected
    for state in ("failed", "canceled", "rejected", "input_required"):
        result.state["a2a_task_state"] = state
        with pytest.raises(ValueError, match="did not complete"):
            validated_partner_result(result)


@pytest.mark.parametrize("lookup", [True, False])
async def test_partner_publishes_only_current_validated_tool_evidence(lookup):
    from common.partner_server import partner_agent, upgrade_quote
    from common.testing import ScriptedModel, tool_message

    agent = partner_agent(load_settings(provider="mock"))
    responses = [tool_message("seat_upgrade", {"flight_id": "FLT-0001"})] if lookup else []
    agent.model = ScriptedModel([*responses, "Wrong flight FLT-000-1, price $1.", "No lookup."])
    if not lookup:
        with pytest.raises(ValueError, match="did not obtain"):
            _ = [event async for event in agent.stream_async("Quote")]
        return
    events = [event async for event in agent.stream_async("Quote")]
    assert len(events) == 1
    assert (
        UpgradeOffer.model_validate_json(str(events[0]["result"])).model_dump() == upgrade_quote()
    )
    with pytest.raises(ValueError, match="did not obtain"):
        _ = [event async for event in agent.stream_async("Another quote without a lookup")]
