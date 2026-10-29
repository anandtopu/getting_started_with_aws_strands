"""Attach one-based page provenance to each extracted PDF page.

Run: uv run python modules/03_conversations/exercises/02_pages.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return "\n".join(value)


def main() -> None:
    print(solve(["Policy A", "Policy B"]))


if __name__ == "__main__":
    main()
