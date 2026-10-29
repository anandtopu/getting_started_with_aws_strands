"""Remove every preference and session record owned by one user, preserving other users.

Run: uv run python modules/09_memory/exercises/03_deletion.py
Expected: sample output; check with the module exercise tests.
Cost/resources: local Python only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline.
    return value["records"]


def main() -> None:
    print(
        solve(
            {
                "delete": "a",
                "records": {
                    "preferences": [{"owner": "a"}, {"owner": "b"}],
                    "sessions": [{"owner": "a"}],
                },
            }
        )
    )


if __name__ == "__main__":
    main()
