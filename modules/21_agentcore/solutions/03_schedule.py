"""Enable a schedule only after traces are reviewed and the cost owner explicitly enables it.

Run: uv run python modules/21_agentcore/solutions/03_schedule.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return value["enabled"] is True and value["reviewed"] is True and value["synthetic"] is True


def main() -> None:
    print(solve({"enabled": True, "reviewed": True, "synthetic": True}))


if __name__ == "__main__":
    main()
