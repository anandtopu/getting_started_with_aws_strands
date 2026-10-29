"""Flag a full recent window with fewer than the required unique agents.

Run: uv run python modules/16_swarms/solutions/02_repetition.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return (
        len(value["history"]) >= value["window"]
        and len(set(value["history"][-value["window"] :])) < value["minimum"]
    )


def main() -> None:
    print(solve({"history": ["a", "b", "a", "b"], "window": 4, "minimum": 3}))


if __name__ == "__main__":
    main()
