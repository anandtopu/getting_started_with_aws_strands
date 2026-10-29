"""Authorize a booking only when a trusted, nonempty customer ID matches the owner.

Run: uv run python modules/05_building_tools/solutions/02_identity.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return bool(value.get("customer_id")) and value["customer_id"] == value.get("owner_id")


def main() -> None:
    print(solve({"customer_id": "CUS-001", "owner_id": "CUS-001"}))


if __name__ == "__main__":
    main()
