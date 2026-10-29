"""Fuse two ranked ID lists with reciprocal rank weights 1/(60+rank), deduplicating IDs.

Run: uv run python modules/08_advanced_rag/exercises/02_fusion.py
Expected: sample output; check with the module exercise tests.
Cost/resources: local Python only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline.
    return value[0]


def main() -> None:
    print(solve([["a", "b"], ["b", "c"]]))


if __name__ == "__main__":
    main()
