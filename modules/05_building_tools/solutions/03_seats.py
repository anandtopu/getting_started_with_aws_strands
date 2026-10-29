"""Allow one through nine travelers only when enough seats remain.

Run: uv run python modules/05_building_tools/solutions/03_seats.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return 1 <= value["travelers"] <= 9 and value["travelers"] <= value["seats"]


def main() -> None:
    print(solve({"travelers": 2, "seats": 2}))


if __name__ == "__main__":
    main()
