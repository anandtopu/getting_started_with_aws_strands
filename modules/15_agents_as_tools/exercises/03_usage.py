"""Sum parent and child per-call token usage exactly once.

Run: uv run python modules/15_agents_as_tools/exercises/03_usage.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return value["parent"]


def main() -> None:
    print(solve({"parent": 240, "children": [120, 120, 120]}))


if __name__ == "__main__":
    main()
