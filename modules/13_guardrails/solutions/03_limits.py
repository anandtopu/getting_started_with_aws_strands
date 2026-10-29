"""Permit a new call only before both the tool budget and deadline are exhausted.

Run: uv run python modules/13_guardrails/solutions/03_limits.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return value["calls"] < value["maximum"] and value["now"] < value["deadline"]


def main():
    print(solve({"calls": 1, "maximum": 2, "now": 9, "deadline": 10}))


if __name__ == "__main__":
    main()
