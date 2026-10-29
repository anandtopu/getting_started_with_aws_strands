"""Apply each request ID at most once while preserving first-seen order.

Run: uv run python modules/12_interrupts/exercises/03_replay.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return value


def main():
    print(solve(["r1", "r2", "r1"]))


if __name__ == "__main__":
    main()
