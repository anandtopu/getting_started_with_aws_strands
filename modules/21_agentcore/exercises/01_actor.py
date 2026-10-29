"""Bind Memory actor to the verified token subject; ignore requested actor IDs.

Run: uv run python modules/21_agentcore/exercises/01_actor.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return value["requested_actor"]


def main() -> None:
    print(solve({"verified_sub": "traveler-a", "requested_actor": "traveler-b"}))


if __name__ == "__main__":
    main()
