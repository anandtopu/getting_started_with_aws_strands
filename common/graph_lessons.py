"""Small runnable Graph topologies, including bounded cycles and nested patterns."""

from strands.multiagent import GraphBuilder

from common.coordination import FunctionNode, worker
from common.swarm_lessons import itinerary_swarm


def basics(settings, *, nested=None):
    builder = GraphBuilder()
    first = worker(
        settings,
        "research",
        ["Synthetic Porto evidence collected."],
        prompt="Outline synthetic Porto trip research in at most 100 words. "
        "Mark unknown dates and prices; never book or pay.",
    )
    if nested == "swarm":
        first = itinerary_swarm(settings)
    elif nested == "graph":
        first = basics(settings)
    builder.add_node(first, "research")
    builder.add_node(
        worker(
            settings,
            "writer",
            ["Draft only; verify dates and occupancy."],
            prompt="Write a trip draft in at most 100 words using the supplied research. "
            "Keep unknown facts explicit. Never book or pay.",
        ),
        "writer",
    )
    builder.add_edge("research", "writer")
    builder.set_entry_point("research")
    builder.set_max_node_executions(2)
    builder.set_execution_timeout(30)
    builder.set_node_timeout(20)
    return builder.build()


def bounded_loop(*, maximum=3):
    state = {"attempts": 0}

    async def revise(task, invocation_state):
        state["attempts"] += 1
        return {"attempt": state["attempts"], "within_budget": False}

    builder = GraphBuilder()
    builder.add_node(FunctionNode("revise", revise), "revise")
    builder.add_edge("revise", "revise", lambda _: True)
    builder.set_entry_point("revise")
    builder.set_max_node_executions(maximum)
    builder.set_execution_timeout(5)
    builder.set_node_timeout(2)
    return builder.build(), state
