"""Project telemetry onto numeric usage only; booleans are not counters.

Run: uv run python modules/19_observability/exercises/01_redact.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return value


def main() -> None:
    print(solve({"gen_ai.usage.input_tokens": 100, "prompt": "private", "gen_ai.usage.flag": True}))


if __name__ == "__main__":
    main()
