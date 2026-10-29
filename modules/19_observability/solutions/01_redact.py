"""Project telemetry onto numeric usage only; booleans are not counters.

Run: uv run python modules/19_observability/solutions/01_redact.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return {
        k: v for k, v in value.items() if k.startswith("gen_ai.usage.") and type(v) in (int, float)
    }


def main() -> None:
    print(solve({"gen_ai.usage.input_tokens": 100, "prompt": "private", "gen_ai.usage.flag": True}))


if __name__ == "__main__":
    main()
