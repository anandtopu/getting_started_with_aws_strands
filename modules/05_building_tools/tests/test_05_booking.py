"""Business tool boundaries survive malicious or mistaken model inputs."""

import runpy
import sqlite3
from contextlib import closing

import pytest
from strands import Agent, ToolContext

from common.config import ROOT
from common.data import data_path
from common.models import get_model
from common.tools.booking import check_seat_availability, get_booking, search_flights


def context(customer):
    agent = Agent(model=get_model(provider="mock", responses=[]), callback_handler=None)
    return ToolContext(
        tool_use={"name": "get_booking", "toolUseId": "test", "input": {}},
        agent=agent,
        invocation_state={"customer_id": customer},
    )


def test_customer_scope_and_sql_parameterization():
    assert get_booking("BKG-0001", context("CUS-001"))["total_cents"] == 70800
    for booking, customer in [("BKG-0001", "CUS-002"), ("' OR 1=1 --", "CUS-001")]:
        with pytest.raises(ValueError, match="unavailable"):
            get_booking(booking, context(customer))
    with pytest.raises(PermissionError):
        get_booking("BKG-0001", context(None))


def test_inventory_bounds_and_no_results():
    assert search_flights("No such city") == []
    assert 0 < len(search_flights("Lisbon")) <= 5
    with pytest.raises(ValueError):
        check_seat_availability("FLT-0001", 0)
    with pytest.raises(ValueError):
        search_flights("Lisbon", -1)


def test_shared_connection_survives_sdk_thread_boundary():
    source = runpy.run_path(str(ROOT / "modules/05_building_tools/examples/05_resource_sharing.py"))
    with closing(
        sqlite3.connect(
            data_path("bookings.db").as_uri() + "?mode=ro", uri=True, check_same_thread=False
        )
    ) as connection:
        desk = source["BookingDesk"](connection)
        agent = Agent(
            model=get_model(provider="mock", responses=[]),
            tools=[desk.booking_total],
            callback_handler=None,
        )
        result = agent.tool.booking_total(booking_id="BKG-0001")
        assert result["status"] == "success"
        assert "70800" in str(result["content"])
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            connection.execute("DELETE FROM bookings")


def test_manual_loop_rejects_unknown_tool_and_bounds_repeats():
    source = runpy.run_path(
        str(ROOT / "modules/05_building_tools/examples/09_manual_converse_loop.py")
    )

    class UnexpectedTool:
        def converse(self, **kwargs):
            return {
                "output": {
                    "message": {
                        "role": "assistant",
                        "content": [
                            {"toolUse": {"name": "delete_booking", "input": {}, "toolUseId": "bad"}}
                        ],
                    }
                },
                "stopReason": "tool_use",
            }

    with pytest.raises(ValueError, match="not allowed"):
        source["manual_loop"](UnexpectedTool(), "fixture")
