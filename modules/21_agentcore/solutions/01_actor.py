"""Bind Memory actor to the verified token subject; ignore requested actor IDs.

Run: uv run python modules/21_agentcore/solutions/01_actor.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return value["verified_sub"]


def main() -> None:
    print(solve({"verified_sub": "traveler-a", "requested_actor": "traveler-b"}))


if __name__ == "__main__":
    main()
