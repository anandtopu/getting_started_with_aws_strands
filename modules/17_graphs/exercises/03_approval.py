"""Require recorded approval, a matching fingerprint, and an unexpired review.

Run: uv run python modules/17_graphs/exercises/03_approval.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return value["decision"] == "approve"


def main() -> None:
    print(
        solve({"decision": "approve", "fingerprint": "a", "current": "a", "now": 1, "expires": 2})
    )


if __name__ == "__main__":
    main()
