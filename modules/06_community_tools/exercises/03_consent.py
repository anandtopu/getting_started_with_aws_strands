"""Accept only an explicit case-insensitive yes after stripping whitespace; missing input denies.

Run: uv run python modules/06_community_tools/exercises/03_consent.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return bool(value)


def main() -> None:
    print(solve(" YES "))


if __name__ == "__main__":
    main()
