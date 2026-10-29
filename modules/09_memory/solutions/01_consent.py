"""Allow only explicitly consented seat/meal fields with known values; deny arbitrary data.

Run: uv run python modules/09_memory/solutions/01_consent.py
Expected: sample output; check with the module exercise tests.
Cost/resources: local Python only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: check the complete contract, including rejection cases.
    choices = {"seat": {"aisle", "window"}, "meal": {"standard", "vegetarian"}}
    return value.get("consent") is True and value.get("value") in choices.get(
        value.get("name"), set()
    )


def main() -> None:
    print(solve({"consent": True, "name": "seat", "value": "aisle"}))


if __name__ == "__main__":
    main()
