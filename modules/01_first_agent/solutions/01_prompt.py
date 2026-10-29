"""Compose an explicit role, constraint, tone and output format from the supplied fields.

Run: uv run python modules/01_first_agent/solutions/01_prompt.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return (
        f"Role: {value['role']}. Constraint: {value['constraint']}. "
        f"Tone: {value['tone']}. Format: {value['format']}."
    )


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
