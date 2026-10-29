"""Deduplicate normalized query strings and keep at most three nonempty queries.

Run: uv run python modules/08_advanced_rag/solutions/01_query_budget.py
Expected: sample output; check with the module exercise tests.
Cost/resources: local Python only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: check the complete contract, including rejection cases.
    return list(dict.fromkeys(q.strip().lower() for q in value if q.strip()))[:3]


def main() -> None:
    print(solve([" Refund ", "refund", "approval", "meal", "budget"]))


if __name__ == "__main__":
    main()
