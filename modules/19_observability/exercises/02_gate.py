"""Fail closed when any evaluation failed, is missing, or scored below 0.8.

Run: uv run python modules/19_observability/exercises/02_gate.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return True


def main() -> None:
    print(solve([{"passed": True, "score": 0.8}]))


if __name__ == "__main__":
    main()
