"""Return new, replay, or conflict by comparing a key with its stored flight terms.

Run: uv run python modules/14_mcp/exercises/03_idempotency.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return "new"


def main():
    print(solve({"stored": {}, "key": "k", "flight": "f1"}))


if __name__ == "__main__":
    main()
