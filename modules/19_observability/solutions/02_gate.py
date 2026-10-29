"""Fail closed when any evaluation failed, is missing, or scored below 0.8.

Run: uv run python modules/19_observability/solutions/02_gate.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return bool(value) and all(
        row.get("passed") is True
        and isinstance(row.get("score"), (int, float))
        and row["score"] >= 0.8
        for row in value
    )


def main() -> None:
    print(solve([{"passed": True, "score": 0.8}]))


if __name__ == "__main__":
    main()
