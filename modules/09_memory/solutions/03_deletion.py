"""Remove every preference and session record owned by one user, preserving other users.

Run: uv run python modules/09_memory/solutions/03_deletion.py
Expected: sample output; check with the module exercise tests.
Cost/resources: local Python only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: check the complete contract, including rejection cases.
    return {
        kind: [r for r in rows if r["owner"] != value["delete"]]
        for kind, rows in value["records"].items()
    }


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
