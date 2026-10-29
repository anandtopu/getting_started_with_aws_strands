"""Compose an explicit role, constraint, tone and output format from the supplied fields.

Run: uv run python modules/01_first_agent/exercises/01_prompt.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return "You are Nimbus."


def main() -> None:
    print(
        solve(
            {
                "role": "Nimbus",
                "constraint": "Use policy only",
                "tone": "Concise",
                "format": "One paragraph",
            }
        )
    )


if __name__ == "__main__":
    main()
