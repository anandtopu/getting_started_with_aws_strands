"""Require every branch, authoritative totals, and an honest budget refusal."""

import json
from pathlib import Path

import pytest

from common.capstone_trip import plan_events
from common.config import load_settings
from common.trip_planning import TripRequest


@pytest.mark.parametrize(
    "case", json.loads((Path(__file__).parents[1] / "evaluation.json").read_text())
)
async def test_evaluation(case):
    events = [
        e
        async for e in plan_events(
            load_settings(provider="mock"), TripRequest(budget_cents=case["budget_cents"])
        )
    ]
    result = events[-1]["result"]
    assert result["budget"] == {
        "total_cents": case["expected_total"],
        "within_budget": case["within_budget"],
    }
    assert set(result["evidence"]) == {"flight", "hotel", "weather"}
    assert {record["role"] for record in result["usage"]} == {
        "flight",
        "hotel",
        "weather",
        "budget",
    }
    assert len([e for e in events if e.get("progress") == "multiagent_node_start"]) == 4
    assert events[-1]["booked"] is False


def test_streamlit_result_and_over_budget():
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(Path(__file__).parents[1] / "solution/app.py")).run()
    app.number_input[0].set_value(100).run()
    app.button[0].click().run(timeout=30)
    assert not app.exception
    assert "exceeds" in app.warning[0].value
