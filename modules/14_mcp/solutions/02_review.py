"""Reject an unexpected tool inventory, including hidden additional pages.

Run: uv run python modules/14_mcp/solutions/02_review.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return not value["next_page"] and set(value["actual"]) == set(value["expected"])


def main():
    print(solve({"actual": ["search"], "expected": ["search"], "next_page": False}))


if __name__ == "__main__":
    main()
