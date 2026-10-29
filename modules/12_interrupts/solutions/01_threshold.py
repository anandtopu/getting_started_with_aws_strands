"""Require approval above $500 or for a change to a non-refundable fare.

Run: uv run python modules/12_interrupts/solutions/01_threshold.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return value["cents"] > 50000 or (value["action"] == "change" and value["nonrefundable"])


def main():
    print(solve({"cents": 50000, "action": "refund", "nonrefundable": True}))


if __name__ == "__main__":
    main()
