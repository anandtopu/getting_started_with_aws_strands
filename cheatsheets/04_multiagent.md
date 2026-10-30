# Tier 4 | Multi-agent systems

Modules 15-18. [Printable PDF](../output/pdf/04_multiagent.pdf).

## Choose a pattern

One agent for a narrow task. Agents as tools for delegation. Graph for explicit dependencies. Swarm for bounded handoffs. A2A for independent remote agents.

## Graph design

Name each node and its contract. Join independent evidence before computing totals. Set node execution, task and time limits. Return partial failure explicitly.

## Delegation boundary

Give each specialist only its tools and required context. Validate specialist output against original evidence. Recalculate money in host code.

## A2A trust

Read the agent card, authenticate the transport, check supported protocol, stream task status, validate artifacts and close owned processes. A card alone grants no trust.

## Partner install

uv sync --group multiagent --group partner
uv run python checkpoints/04_trip_planning_crew/solution.py --mock --decision approve

## Costs and concurrency

Count every specialist call and retry. Parallel work can reduce latency while increasing total cost. A shared budget must cover the entire request.

## Test independently

Use held-out flights, budgets and malformed partner artifacts. Test timeouts, cross-user access and duplicate approval; do not grade a result only with its own producer.

## Checkpoint

Build a bounded planning crew, show verified totals and a reviewed draft, then demonstrate an actual separate-process partner. No travel purchase is performed.

See [the feature map](../docs/FEATURE_MAP.md) for source examples and [costs](../docs/COSTS.md) for live pricing.
