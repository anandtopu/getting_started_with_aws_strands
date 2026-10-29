"""Accept only an approved, unexpired request belonging to the trusted owner.

Run: uv run python modules/12_interrupts/solutions/02_expiry.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return (
        value["status"] == "approved"
        and value["owner"] == value["trusted_owner"]
        and value["expires"] > value["now"]
    )


def main():
    print(
        solve({"status": "approved", "owner": "a", "trusted_owner": "a", "expires": 11, "now": 10})
    )


if __name__ == "__main__":
    main()
