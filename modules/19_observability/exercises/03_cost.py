"""Compute dollars from token counts and per-million prices without rounding each call.

Run: uv run python modules/19_observability/exercises/03_cost.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return 0


def main() -> None:
    print(solve({"input": 1000, "output": 100, "input_rate": 1, "output_rate": 5}))


if __name__ == "__main__":
    main()
