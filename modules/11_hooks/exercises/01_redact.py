"""Recursively redact email and US phone patterns without mutating the input.

Run: uv run python modules/11_hooks/exercises/01_redact.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return value


def main():
    print(solve({"message": ["a@example.com", "555-123-4567"]}))


if __name__ == "__main__":
    main()
