"""Four bounded specialists in an actual Graph with visible streaming progress."""

import asyncio
import json

import httpx
from pydantic import BaseModel, Field
from strands.multiagent import GraphBuilder

from common.coordination import FunctionNode, worker
from common.specialists import specialist
from common.testing import tool_message
from common.trip_planning import TripRequest


class Weather(BaseModel):
    temperature_c: float
    scope: str


class Budget(BaseModel):
    total_cents: int = Field(ge=0)
    within_budget: bool


def planner(settings, request: TripRequest):
    state = {"evidence": {}, "usage": []}
    graph = GraphBuilder()

    async def catalog_node(role):
        answer = await specialist(settings, role, request, state["usage"])
        state["evidence"][role] = answer
        return answer

    async def flight(task, invocation_state):
        return await catalog_node("flight")

    async def hotel(task, invocation_state):
        return await catalog_node("hotel")

    async def weather(task, invocation_state):
        coordinates = {
            "Porto": (41.15, -8.61),
            "Chicago": (41.88, -87.63),
            "Lima": (-12.05, -77.04),
        }
        lat, lon = coordinates[request.city]
        transport = httpx.MockTransport(
            lambda req: httpx.Response(200, json={"current": {"temperature_2m": 18.5}})
        )
        async with httpx.AsyncClient(
            transport=transport if settings.provider == "mock" else None,
            timeout=10,
            follow_redirects=False,
            trust_env=False,
        ) as client:
            response = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={"latitude": lat, "longitude": lon, "current": "temperature_2m"},
            )
            response.raise_for_status()
            evidence = {
                "temperature_c": response.json()["current"]["temperature_2m"],
                "scope": "fixture"
                if settings.provider == "mock"
                else "current weather, NOT a future trip forecast",
            }
        agent = worker(
            settings,
            "weather",
            [tool_message("Weather", evidence)],
            structured_output_model=Weather,
        )
        result = await agent.invoke_async(json.dumps(evidence), limits={"turns": 2})
        if result.structured_output.model_dump() != evidence:
            raise ValueError("Weather specialist changed source evidence")
        state["usage"].append({"role": "weather", "usage": dict(result.metrics.accumulated_usage)})
        state["evidence"]["weather"] = evidence
        return evidence

    async def budget(task, invocation_state):
        total = sum(state["evidence"][role]["cents"] for role in ("flight", "hotel"))
        expected = {"total_cents": total, "within_budget": total <= request.budget_cents}
        agent = worker(
            settings, "budget", [tool_message("Budget", expected)], structured_output_model=Budget
        )
        result = await agent.invoke_async(json.dumps(expected), limits={"turns": 2})
        if result.structured_output.model_dump() != expected:
            raise ValueError("Budget specialist changed authoritative arithmetic")
        state["usage"].append({"role": "budget", "usage": dict(result.metrics.accumulated_usage)})
        state["budget"] = expected
        return expected

    for name, function in (
        ("flight", flight),
        ("hotel", hotel),
        ("weather", weather),
        ("budget", budget),
    ):
        graph.add_node(FunctionNode(name, function), name)
    for name in ("flight", "hotel", "weather"):
        graph.set_entry_point(name)
        graph.add_edge(name, "budget")
    graph.set_max_node_executions(4)
    graph.set_execution_timeout(45)
    graph.set_node_timeout(20)
    return graph.build(), state


async def plan_events(settings, request=None):
    graph, state = planner(settings, request or TripRequest())
    async with asyncio.timeout(50):
        async for event in graph.stream_async("Prepare the reviewed Nimbus trip request."):
            if event.get("type") in {"multiagent_node_start", "multiagent_node_stop"}:
                yield {"progress": event["type"], "node": event.get("node_id")}
    if "budget" not in state or len(state["evidence"]) != 3:
        raise ValueError("Trip graph did not complete every required branch")
    yield {
        "result": state,
        "booked": False,
        "limitations": "One-way flight; one room; verify occupancy and future weather.",
    }
