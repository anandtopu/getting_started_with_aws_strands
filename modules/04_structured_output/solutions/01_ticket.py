"""Validate a ticket with the real TicketTriage schema and return whether it is valid.

Run: uv run python modules/04_structured_output/solutions/01_ticket.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    from pydantic import ValidationError

    from common.schemas import TicketTriage

    try:
        TicketTriage.model_validate(value)
        return True
    except ValidationError:
        return False


def main() -> None:
    print(solve({"category": "refund", "urgency": "normal", "summary": "Refund needed"}))


if __name__ == "__main__":
    main()
