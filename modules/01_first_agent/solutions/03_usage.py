"""Sum inputTokens and outputTokens across model turns; missing counts are zero.

Run: uv run python modules/01_first_agent/solutions/03_usage.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return {key: sum(turn.get(key, 0) for turn in value) for key in ("inputTokens", "outputTokens")}


def main() -> None:
    print(solve([{"inputTokens": 100, "outputTokens": 20}, {"inputTokens": 160}]))


if __name__ == "__main__":
    main()
