"""Split words into overlapping windows; reject non-progressing settings.

Run: uv run python modules/07_rag/exercises/01_chunks.py
Expected: sample output; check with the module exercise tests.
Cost/resources: local Python only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline.
    return [value["text"]]


def main() -> None:
    print(solve({"text": "one two three four five", "size": 3, "overlap": 1}))


if __name__ == "__main__":
    main()
