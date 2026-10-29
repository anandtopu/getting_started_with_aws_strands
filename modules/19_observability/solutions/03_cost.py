"""Compute dollars from token counts and per-million prices without rounding each call.

Run: uv run python modules/19_observability/solutions/03_cost.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return (value["input"] * value["input_rate"] + value["output"] * value["output_rate"]) / 1000000


def main() -> None:
    print(solve({"input": 1000, "output": 100, "input_rate": 1, "output_rate": 5}))


if __name__ == "__main__":
    main()
