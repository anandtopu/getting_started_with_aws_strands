"""Concatenate only text content blocks from an assistant message.

Run: uv run python modules/01_first_agent/exercises/02_message.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return str(value)


def main() -> None:
    print(solve({"content": [{"text": "Hello "}, {"toolUse": {}}, {"text": "Nimbus"}]}))


if __name__ == "__main__":
    main()
