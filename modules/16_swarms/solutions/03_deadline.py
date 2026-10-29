"""Return whether another node can start before both the visit limit and deadline.

Run: uv run python modules/16_swarms/solutions/03_deadline.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return value["visits"] < value["maximum"] and value["now"] < value["deadline"]


def main() -> None:
    print(solve({"visits": 1, "maximum": 2, "now": 9, "deadline": 10}))


if __name__ == "__main__":
    main()
