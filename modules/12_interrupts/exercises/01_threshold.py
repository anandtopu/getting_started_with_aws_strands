"""Require approval above $500 or for a change to a non-refundable fare.

Run: uv run python modules/12_interrupts/exercises/01_threshold.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return False


def main():
    print(solve({"cents": 50000, "action": "refund", "nonrefundable": True}))


if __name__ == "__main__":
    main()
