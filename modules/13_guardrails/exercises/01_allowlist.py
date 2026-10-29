"""Filter requested capabilities using a reviewed allow-list; deduplicate in order.

Run: uv run python modules/13_guardrails/exercises/01_allowlist.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return value["requested"]


def main():
    print(solve({"requested": ["read", "export", "read"], "allowed": ["read"]}))


if __name__ == "__main__":
    main()
