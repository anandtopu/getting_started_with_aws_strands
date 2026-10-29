"""Convert a list of traveler strings into SDK text content blocks.

Run: uv run python modules/03_conversations/solutions/03_content.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return [{"text": text} for text in value]


def main() -> None:
    print(solve(["Lisbon", "Budget 600"]))


if __name__ == "__main__":
    main()
