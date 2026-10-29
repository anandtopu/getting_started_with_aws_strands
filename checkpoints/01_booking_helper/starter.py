"""A runnable search-only baseline for the Tier 1 booking checkpoint.

Run: uv run python checkpoints/01_booking_helper/starter.py --mock
Expected: synthetic Lisbon flight candidates; no reservation or AWS resources.
Cost: $0. Concepts: read-only tools; extend to a structured agent in the exercise.
"""

from common.lessons import complete, lesson_settings
from common.pretty import console, run_cli
from common.tools.booking import search_flights


def main() -> None:
    lesson_settings()
    candidates = search_flights("Lisbon")
    console.print(candidates)
    # YOUR CODE HERE: compose all four tools, supply identity outside the prompt,
    # request an Itinerary, cap turns and validate its prices against inventory.
    complete()


if __name__ == "__main__":
    run_cli(main)
