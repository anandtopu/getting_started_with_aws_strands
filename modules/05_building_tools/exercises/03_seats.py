"""Allow one through nine travelers only when enough seats remain.

Run: uv run python modules/05_building_tools/exercises/03_seats.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return value["seats"] > 0


def main() -> None:
    print(solve({"travelers": 2, "seats": 2}))


if __name__ == "__main__":
    main()
