"""Deduplicate normalized query strings and keep at most three nonempty queries.

Run: uv run python modules/08_advanced_rag/exercises/01_query_budget.py
Expected: sample output; check with the module exercise tests.
Cost/resources: local Python only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline.
    return value


def main() -> None:
    print(solve([" Refund ", "refund", "approval", "meal", "budget"]))


if __name__ == "__main__":
    main()
