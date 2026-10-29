"""Return only the trusted owner's unexpired records; expiry is exclusive.

Run: uv run python modules/09_memory/exercises/02_retention.py
Expected: sample output; check with the module exercise tests.
Cost/resources: local Python only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline.
    return value["rows"]


def main() -> None:
    print(
        solve(
            {
                "owner": "a",
                "now": 100,
                "rows": [
                    {"owner": "a", "expires": 101},
                    {"owner": "b", "expires": 999},
                    {"owner": "a", "expires": 100},
                ],
            }
        )
    )


if __name__ == "__main__":
    main()
