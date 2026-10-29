"""Sum inputTokens and outputTokens across model turns; missing counts are zero.

Run: uv run python modules/01_first_agent/exercises/03_usage.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return {"inputTokens": 0, "outputTokens": 0}


def main() -> None:
    print(solve([{"inputTokens": 100, "outputTokens": 20}, {"inputTokens": 160}]))


if __name__ == "__main__":
    main()
