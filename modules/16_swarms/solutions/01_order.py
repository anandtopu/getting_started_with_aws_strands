"""Extract visited node IDs in order, retaining repeated visits.

Run: uv run python modules/16_swarms/solutions/01_order.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return [node["node_id"] for node in value]


def main() -> None:
    print(solve([{"node_id": "researcher"}, {"node_id": "writer"}, {"node_id": "researcher"}]))


if __name__ == "__main__":
    main()
