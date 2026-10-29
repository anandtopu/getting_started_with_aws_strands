"""Require recorded approval, a matching fingerprint, and an unexpired review.

Run: uv run python modules/17_graphs/solutions/03_approval.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return (
        value["decision"] == "approve"
        and value["fingerprint"] == value["current"]
        and value["now"] < value["expires"]
    )


def main() -> None:
    print(
        solve({"decision": "approve", "fingerprint": "a", "current": "a", "now": 1, "expires": 2})
    )


if __name__ == "__main__":
    main()
