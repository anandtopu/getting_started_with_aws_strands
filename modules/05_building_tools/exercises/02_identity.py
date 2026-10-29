"""Authorize a booking only when a trusted, nonempty customer ID matches the owner.

Run: uv run python modules/05_building_tools/exercises/02_identity.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return True


def main() -> None:
    print(solve({"customer_id": "CUS-001", "owner_id": "CUS-001"}))


if __name__ == "__main__":
    main()
