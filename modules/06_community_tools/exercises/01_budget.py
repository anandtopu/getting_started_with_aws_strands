"""Use the checked convert_budget tool and return its displayed conversion.

Run: uv run python modules/06_community_tools/exercises/01_budget.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return value["amount"]


def main() -> None:
    print(solve({"amount": "100", "rate": ".92"}))


if __name__ == "__main__":
    main()
