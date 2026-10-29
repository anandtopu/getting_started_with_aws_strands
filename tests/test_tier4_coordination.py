"""Exercise real SDK routing and host-owned boundaries without external model calls."""

import time

import pytest
from pydantic import ValidationError

from common.config import load_settings
from common.coordination import report
from common.graph_lessons import basics, bounded_loop
from common.specialists import concierge
from common.swarm_lessons import itinerary_swarm, timeout_probe
from common.trip_graph import Quote, TripReview, group_trip_graph, run_group_trip
from common.trip_planning import TripRequest, catalog, validate_offer


@pytest.fixture
def cfg():
    return load_settings(provider="mock")


async def test_delegation_totals_and_minimum_context(cfg):
    single = await concierge(cfg, delegated=False)
    team = await concierge(cfg)
    assert single["usage"]["totalTokens"] == 240
    assert team["usage"]["totalTokens"] == 600
    assert {c["role"] for c in team["children"]} == {"flight", "hotel", "policy"}
    for child in team["children"]:
        assert set(child["context"]) == {"city", "evidence"}
    assert "no semantic quality score" in team["quality_evidence"]


async def test_concurrent_duplicate_specialist_call_does_not_start_another_model(cfg, monkeypatch):
    from common import specialists
    from common.testing import tool_message

    real_worker = specialists.worker
    parents = []

    def duplicate(settings, name, responses, **kwargs):
        if name == "concierge":
            responses[0]["content"] += tool_message("flight_specialist", {}, "duplicate")["content"]
        agent = real_worker(settings, name, responses, **kwargs)
        if name == "concierge":
            parents.append(agent)
        return agent

    monkeypatch.setattr(specialists, "worker", duplicate)
    result = await specialists.concierge(cfg)
    assert len(result["children"]) == 3
    assert result["usage"]["totalTokens"] == 600
    errors = [
        block["toolResult"]
        for message in parents[0].messages
        for block in message["content"]
        if "toolResult" in block and block["toolResult"]["status"] == "error"
    ]
    assert len(errors) == 1
    assert "already called" in str(errors[0])


def test_untrusted_quote_and_request_fail_closed():
    request = TripRequest()
    expected = catalog("flight", request)
    for change in ({"cents": 1}, {"reference": "forged"}, {"role": "hotel"}):
        with pytest.raises(ValueError):
            validate_offer({**expected, **change}, expected)
    for values in ({"travelers": True}, {"budget_cents": -1}, {"passport": "private"}):
        with pytest.raises(ValidationError):
            TripRequest(**values)


def test_swarm_order_and_revisit_accounting(cfg):
    result = itinerary_swarm(cfg)("Make a Porto draft")
    assert result.status.value == "completed"
    assert [n.node_id for n in result.node_history] == [
        "researcher",
        "budget_planner",
        "writer",
        "reviewer",
    ]
    assert result.accumulated_usage["totalTokens"] == 840
    loop = itinerary_swarm(cfg, loop=True)("Repeat")
    assert loop.status.value == "failed"
    assert loop.execution_count == 4
    assert report(loop, cfg)["inference_estimate_usd"] is None


@pytest.mark.parametrize("limits", [{"max_handoffs": 2}, {"max_iterations": 2}])
def test_swarm_execution_ceilings(cfg, limits):
    result = itinerary_swarm(cfg, loop=True, **limits)("Repeat")
    assert result.status.value == "failed"
    assert result.execution_count == 2


@pytest.mark.parametrize("overall", [False, True])
async def test_timeout_cancels_async_tool(cfg, overall):
    result, closed = await timeout_probe(cfg, overall=overall)
    if overall:
        assert result is None
    else:
        assert result.status.value == "failed"
    assert closed == [True]


@pytest.mark.parametrize(
    "decision,budget,node",
    [
        ("approve", 100000, "draft"),
        ("reject", 100000, "rejected"),
        ("approve", 1, "over_budget"),
    ],
)
def test_graph_routes_and_catalog_total(cfg, decision, budget, node):
    result, state = run_group_trip(cfg, decision=decision, budget_cents=budget)
    assert result.status.value == "completed"
    assert node in result.results
    assert state["review"].quote.total_cents == 52800
    assert bool(state["draft"]) is (node == "draft")


def test_parallel_search_and_single_join(cfg):
    graph, state, req = group_trip_graph(cfg, budget_cents=1, search_delay=0.05)
    result = graph(req.model_dump_json())
    a, b = state["intervals"].values()
    assert max(a[0], b[0]) < min(a[1], b[1])
    assert sum(n.node_id == "budget" for n in result.execution_order) == 1


@pytest.mark.parametrize("expired", [False, True])
def test_interrupt_text_cannot_grant_approval(cfg, expired):
    graph, state, req = group_trip_graph(cfg)
    paused = graph(req.model_dump_json())
    assert paused.interrupts
    if expired:
        review = state["review"]
        review.decide("approve", review.quote.fingerprint())
        review.expires = time.time() - 1
    resumed = graph(
        [
            {"interruptResponse": {"interruptId": i.id, "response": "APPROVE"}}
            for i in paused.interrupts
        ]
    )
    assert "rejected" in resumed.results
    assert state["draft"] is None


def test_review_binding_expiry_replay_and_immutable_terms():
    quote = Quote(
        city="Porto", flight_id="f1", hotel_id="h1", total_cents=100, travelers=2, nights=2
    )
    review = TripReview(quote, 10)
    with pytest.raises(ValueError, match="displayed quote"):
        review.decide("approve", "wrong", now=1)
    with pytest.raises(ValidationError):
        quote.total_cents = 0
    review.decide("approve", quote.fingerprint(), now=10)
    assert review.decision == "expired"
    assert not review.approved()
    with pytest.raises(ValueError, match="already"):
        review.decide("approve", quote.fingerprint(), now=1)


def test_loop_and_nested_patterns(cfg):
    graph, state = bounded_loop(maximum=3)
    result = graph("Try")
    assert result.status.value == "failed" and state["attempts"] == 3
    for kind, tokens in [("graph", 360), ("swarm", 960)]:
        nested = basics(cfg, nested=kind)("Draft")
        assert nested.status.value == "completed"
        assert nested.accumulated_usage["totalTokens"] == tokens


def test_checkpoint_specialist_usage_is_propagated(cfg):
    result, state = run_group_trip(cfg, decision="approve", specialist_search=True)
    assert state["draft"] and result.status.value == "completed"
    # Parser + two specialists + approval tool round trip = five fixture model calls.
    assert result.accumulated_usage["totalTokens"] == 600
