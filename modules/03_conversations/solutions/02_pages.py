"""Attach one-based page provenance to each extracted PDF page.

Run: uv run python modules/03_conversations/solutions/02_pages.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return "\n".join(f"[Page {index}] {text}" for index, text in enumerate(value, 1))


def main() -> None:
    print(solve(["Policy A", "Policy B"]))


if __name__ == "__main__":
    main()
