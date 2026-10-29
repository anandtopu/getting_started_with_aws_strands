"""Return new, replay, or conflict by comparing a key with its stored flight terms.

Run: uv run python modules/14_mcp/solutions/03_idempotency.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    existing = value["stored"].get(value["key"])
    return "new" if existing is None else ("replay" if existing == value["flight"] else "conflict")


def main():
    print(solve({"stored": {}, "key": "k", "flight": "f1"}))


if __name__ == "__main__":
    main()
