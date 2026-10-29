"""Deterministic routing, parallel catalog reads, and human review around real agents."""

import asyncio
import hashlib
import time
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict
from strands import tool
from strands.multiagent import GraphBuilder
from strands.types.tools import ToolContext

from common.coordination import FunctionNode, StepOutput, worker
from common.testing import tool_message
from common.trip_planning import TripRequest, catalog


class Quote(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    city: str
    flight_id: str
    hotel_id: str
    total_cents: int
    travelers: int
    nights: int

    def fingerprint(self):
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()


@dataclass
class TripReview:
    quote: Quote
    expires: float
    decision: str | None = None

    def decide(self, decision, fingerprint, *, now=None):
        if self.decision is not None:
            raise ValueError("This review already has a decision")
        if fingerprint != self.quote.fingerprint() or decision not in {"approve", "reject"}:
            raise ValueError("Decision must match the displayed quote")
        self.decision = (
            "expired" if (time.time() if now is None else now) >= self.expires else decision
        )

    def approved(self):
        return self.decision == "approve" and time.time() < self.expires


def group_trip_graph(settings, *, budget_cents=100000, search_delay=0, specialist_search=False):
    request = TripRequest(budget_cents=budget_cents)
    state = {"searches": {}, "intervals": {}, "draft": None, "review": None}
    parser = worker(
        settings,
        "parse",
        [tool_message("TripRequest", request.model_dump())],
        structured_output_model=TripRequest,
        prompt="Parse the user's request exactly. Never increase their budget.",
    )
    builder = GraphBuilder()
    builder.add_node(parser, "parse")

    def parsed():
        value = graph.state.results["parse"].result.structured_output
        # Numeric budget and party limits remain application-owned after model parsing.
        if value is None or value.model_dump() != request.model_dump():
            raise ValueError("Parsed request differs from the host-reviewed request")
        return value

    def search_node(role):
        async def run(task, invocation_state):
            start = time.monotonic()
            await asyncio.sleep(search_delay)  # Optional deterministic overlap probe, no network.
            result = catalog(role, parsed())
            measured = StepOutput(result)
            if specialist_search:
                from common.specialists import specialist

                records = []
                result = await specialist(settings, role, parsed(), records)
                measured = StepOutput(result, records[0]["usage"])
            state["searches"][role] = result
            state["intervals"][role] = (start, time.monotonic())
            return measured

        return FunctionNode(role, run)

    async def budget(task, invocation_state):
        req = parsed()
        flight, hotel = state["searches"]["flight"], state["searches"]["hotel"]
        quote = Quote(
            city=req.city,
            flight_id=flight["reference"],
            hotel_id=hotel["reference"],
            total_cents=flight["cents"] + hotel["cents"],
            travelers=req.travelers,
            nights=req.nights,
        )
        state["review"] = TripReview(quote, time.time() + 300)
        state["within_budget"] = quote.total_cents <= req.budget_cents
        return {"quote": quote.model_dump(), "within_budget": state["within_budget"]}

    @tool(context=True)
    def review_trip(tool_context: ToolContext) -> dict:
        """Pause to review the host's exact quote; a chat response cannot authorize it."""
        review = state["review"]
        tool_context.interrupt(
            "trip-review",
            reason={
                "quote": review.quote.model_dump(),
                "fingerprint": review.quote.fingerprint(),
                "expires": review.expires,
            },
        )
        return {"approved": review.approved(), "decision": review.decision}

    approval = worker(
        settings,
        "approval",
        [tool_message("review_trip", {}), "The application records the review outcome."],
        tools=[review_trip],
        prompt="Call review_trip once and report its recorded result. Never infer approval.",
    )

    async def draft(task, invocation_state):
        review = state["review"]
        if not review.approved():
            raise PermissionError("A current recorded approval is required to draft confirmation")
        quote = review.quote
        # Fixed prose preserves prices and references; composing a draft needs no extra LLM.
        state["draft"] = (
            f"Subject: Review your Porto trip draft\n\nProposed {quote.flight_id} and "
            f"{quote.hotel_id}: ${quote.total_cents / 100:.2f}. "
            "One-way flight and one room only; occupancy, return travel and extras "
            "need confirmation. This email is a draft. Nothing is booked or sent."
        )
        return {"draft": state["draft"]}

    async def declined(task, invocation_state):
        return {"outcome": "No confirmation drafted: over budget or review not approved."}

    for name, node in [
        ("flight", search_node("flight")),
        ("hotel", search_node("hotel")),
        ("budget", FunctionNode("budget", budget)),
        ("approval", approval),
        ("draft", FunctionNode("draft", draft)),
        ("over_budget", FunctionNode("over_budget", declined)),
        ("rejected", FunctionNode("rejected", declined)),
    ]:
        builder.add_node(node, name)
    for a, b in [
        ("parse", "flight"),
        ("parse", "hotel"),
        ("flight", "budget"),
        ("hotel", "budget"),
    ]:
        builder.add_edge(a, b)
    builder.add_edge("budget", "approval", lambda _: state["within_budget"])
    builder.add_edge("budget", "over_budget", lambda _: not state["within_budget"])
    builder.add_edge("approval", "draft", lambda _: state["review"].approved())
    builder.add_edge("approval", "rejected", lambda _: not state["review"].approved())
    builder.set_entry_point("parse")
    builder.set_max_node_executions(10)
    builder.set_execution_timeout(30)
    builder.set_node_timeout(15)
    graph = builder.build()
    return graph, state, request


def run_group_trip(settings, *, decision="reject", budget_cents=100000, specialist_search=False):
    graph, state, request = group_trip_graph(
        settings, budget_cents=budget_cents, specialist_search=specialist_search
    )
    result = graph(request.model_dump_json())
    if result.interrupts:
        review = state["review"]
        if decision == "ask":
            print("Review exact terms:", review.quote.model_dump(), review.quote.fingerprint())
            decision = input("approve/reject: ").strip()
        review.decide(decision, review.quote.fingerprint())
        result = graph(
            [
                {"interruptResponse": {"interruptId": i.id, "response": "decision recorded"}}
                for i in result.interrupts
            ]
        )
    return result, state
