"""Allow only explicitly consented seat/meal fields with known values; deny arbitrary data.

Run: uv run python modules/09_memory/exercises/01_consent.py
Expected: sample output; check with the module exercise tests.
Cost/resources: local Python only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline.
    return bool(value.get("consent"))


def main() -> None:
    print(solve({"consent": True, "name": "seat", "value": "aisle"}))


if __name__ == "__main__":
    main()
