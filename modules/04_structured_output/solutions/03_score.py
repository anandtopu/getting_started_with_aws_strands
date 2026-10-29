"""Return exact-match accuracy over category AND urgency; empty input scores zero.

Run: uv run python modules/04_structured_output/solutions/03_score.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return (
        sum(
            all(
                row["prediction"].get(key) == row["expected"][key]
                for key in ("category", "urgency")
            )
            for row in value
        )
        / len(value)
        if value
        else 0.0
    )


def main() -> None:
    print(
        solve(
            [
                {
                    "prediction": {"category": "refund", "urgency": "normal"},
                    "expected": {"category": "refund", "urgency": "high"},
                },
                {
                    "prediction": {"category": "change", "urgency": "normal"},
                    "expected": {"category": "change", "urgency": "normal"},
                },
            ]
        )
    )


if __name__ == "__main__":
    main()
