"""Filter supplied flights by case-insensitive destination and maximum USD price; return their IDs.

Run: uv run python modules/05_building_tools/solutions/01_search.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return [
        row["id"]
        for row in value["flights"]
        if row["destination"].casefold() == value["destination"].casefold()
        and row["price"] <= value["budget"]
    ]


def main() -> None:
    print(
        solve(
            {
                "destination": "lisbon",
                "budget": 100,
                "flights": [
                    {"id": "A", "destination": "Lisbon", "price": 100},
                    {"id": "B", "destination": "Paris", "price": 90},
                    {"id": "C", "destination": "Lisbon", "price": 101},
                ],
            }
        )
    )


if __name__ == "__main__":
    main()
