"""Real local MCP transports, reservation idempotency and capability review."""

import json
import sqlite3

import httpx
import pytest
from strands import Agent

from common.config import load_settings
from common.mcp_clients import http_booking, reviewed_tools, stdio_booking
from common.models import get_model
from common.testing import tool_message


def test_stdio_agent_reserves_exactly_once(tmp_path):
    path = tmp_path / "mcp.db"
    with stdio_booking(path) as client:
        tools = reviewed_tools(
            client, ["nimbus_search_flights", "nimbus_create_booking", "nimbus_get_booking"]
        )
        args = {"flight_id": "FLT-0001", "idempotency_key": "test-key"}
        agent = Agent(
            model=get_model(
                provider="mock", responses=[tool_message("nimbus_create_booking", args), "Reserved"]
            ),
            tools=tools,
            callback_handler=None,
        )
        agent("Reserve")
        assert client.call_tool_sync("again", "create_booking", args)["status"] == "success"
        wrong = client.call_tool_sync("wrong", "create_booking", {**args, "flight_id": "FLT-0002"})
        assert wrong["status"] == "error"
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT count(*) FROM reservations").fetchone()[0] == 1


@pytest.mark.local_protocol
def test_authenticated_http_and_filter(tmp_path):
    with http_booking(tmp_path / "h.db") as (client, url):
        assert httpx.post(url, json={}).status_code == 401
        assert len(reviewed_tools(client, ["nimbus_search_flights"])) == 1
        with pytest.raises(ValueError):
            reviewed_tools(client, ["nimbus_create_booking"])
        response = client.call_tool_sync("query", "search_flights", {"destination": "Porto"})
        assert response["status"] == "success"
        assert "FLT-0001" in json.dumps(response)
    with pytest.raises((httpx.ConnectError, httpx.ConnectTimeout)):
        httpx.get(url, timeout=1)


def test_pricing_agent_uses_host_bounded_mcp_request():
    from common.pricing_agent import lambda_cost_question

    class ContractClient:
        calls = []

        def call_tool_sync(self, call_id, name, arguments):
            self.calls.append((call_id, name, arguments))
            return {"status": "success", "content": [{"text": "Incomplete pricing evidence"}]}

    client = ContractClient()
    result = lambda_cost_question(load_settings(provider="mock"), client=client)
    assert result.stop_reason == "end_turn"
    assert len(client.calls) == 1
    _, name, arguments = client.calls[0]
    assert name == "get_pricing"
    assert arguments["service_code"] == "AWSLambda"
    assert arguments["max_results"] == 10
    assert arguments["max_allowed_characters"] == 10000
