"""Validate a ticket with the real TicketTriage schema and return whether it is valid.

Run: uv run python modules/04_structured_output/exercises/01_ticket.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return True


def main() -> None:
    print(solve({"category": "refund", "urgency": "normal", "summary": "Refund needed"}))


if __name__ == "__main__":
    main()
