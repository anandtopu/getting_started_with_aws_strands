"""Normalize a provider name and accept only the five supported live providers.

Run: uv run python modules/00_setup/exercises/01_provider.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return bool(value)


def main() -> None:
    print(solve(" OLLAMA "))


if __name__ == "__main__":
    main()
