"""Bounded real Swarm runs with deterministic handoff fixtures."""

import asyncio

from strands import tool
from strands.multiagent import Swarm

from common.coordination import worker
from common.testing import tool_message


def itinerary_swarm(settings, *, loop=False, **limits):
    names = ["researcher", "budget_planner", "writer", "reviewer"]
    if loop:
        names = ["researcher", "reviewer"]
    agents = []
    notes = {
        "researcher": "Porto: riverside walk on day 1, historic centre on day 2.",
        "budget_planner": "Catalog subtotal $528; excludes return flight, meals and extras.",
        "writer": "Day 1: riverside walk. Day 2: historic centre. Confirm accessibility and hours.",
        "reviewer": "Two-day Porto draft reviewed. Confirm room occupancy and return travel.",
    }
    for index, name in enumerate(names):
        target = names[(index + 1) % len(names)]
        responses = [notes[name] + " No booking or payment authorized."]
        if loop or index < len(names) - 1:
            pair = [
                tool_message(
                    "handoff_to_agent",
                    {
                        "agent_name": target,
                        "message": f"Continue the Porto draft as {target}.",
                        "context": {
                            "destination": "Porto",
                            "budget_cents": 100000,
                            "scope": "draft only",
                            "draft_notes": notes[name],
                        },
                    },
                    f"handoff-{index}",
                ),
                notes[name] + f" Passing the public draft to {target}.",
            ]
            responses = pair * (4 if loop else 1)
        instruction = (
            f"Do your role's work, then hand off to {target} once via handoff_to_agent "
            "with concise evidence in context. Finish your turn after the handoff."
            if loop or index < len(names) - 1
            else "Review the draft, state unresolved assumptions, and finish without handing off."
        )
        agents.append(
            worker(
                settings,
                name,
                responses,
                prompt=f"You are {name}. Work only on the public Porto draft. " + instruction,
            )
        )
    bounds = dict(
        max_handoffs=6,
        max_iterations=6,
        execution_timeout=30,
        node_timeout=10,
        repetitive_handoff_detection_window=4,
        repetitive_handoff_min_unique_agents=3,
    )
    bounds.update(limits)
    return Swarm(agents, entry_point=agents[0], **bounds)


async def timeout_probe(settings, *, overall=False):
    """Exercise cooperative cancellation inside a real async tool, with no external call."""
    closed = []

    @tool
    async def slow_catalog() -> str:
        """Wait for a deliberately slow local catalog fixture."""
        try:
            await asyncio.sleep(5)
            return "Catalog ready"
        finally:
            closed.append(True)

    node = worker(
        settings,
        "slow",
        [tool_message("slow_catalog", {}), "Done"],
        tools=[slow_catalog],
        prompt="Call slow_catalog once.",
    )
    swarm = Swarm(
        [node],
        max_handoffs=2,
        max_iterations=2,
        node_timeout=10 if overall else 0.05,
        execution_timeout=0.05 if overall else 10,
    )
    try:
        # SDK execution_timeout is checked between nodes; wrap for a hard host deadline.
        async with asyncio.timeout(0.05 if overall else 15):
            result = await swarm.invoke_async("Read the slow catalog")
    except TimeoutError:
        result = None
    return result, closed
