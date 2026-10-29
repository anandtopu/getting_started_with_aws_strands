"""Calculate USD from input/output counts and per-million prices; round to six decimals.

Run: uv run python modules/00_setup/solutions/02_tokens.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return round(
        (value["input"] * value["input_price"] + value["output"] * value["output_price"])
        / 1_000_000,
        6,
    )


def main() -> None:
    print(solve({"input": 2000, "output": 500, "input_price": 0.3, "output_price": 2.5}))


if __name__ == "__main__":
    main()
