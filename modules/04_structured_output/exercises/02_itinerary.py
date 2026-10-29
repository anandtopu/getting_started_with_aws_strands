"""Validate nested flight legs and their total with the Itinerary schema.

Run: uv run python modules/04_structured_output/exercises/02_itinerary.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return True


def main() -> None:
    print(
        solve(
            {
                "traveler": "Demo",
                "legs": [{"flight_id": "FLT-0001", "destination": "Lisbon", "price_cents": 100}],
                "total_cents": 100,
            }
        )
    )


if __name__ == "__main__":
    main()
