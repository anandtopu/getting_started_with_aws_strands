"""Calculate USD from input/output counts and per-million prices; round to six decimals.

Run: uv run python modules/00_setup/exercises/02_tokens.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return 0.0


def main() -> None:
    print(solve({"input": 2000, "output": 500, "input_price": 0.3, "output_price": 2.5}))


if __name__ == "__main__":
    main()
