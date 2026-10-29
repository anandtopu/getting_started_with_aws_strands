"""Return unknown if any agent omits its usage; otherwise sum reported totals.

Run: uv run python modules/18_a2a/solutions/03_usage_unknown.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return None if any(n is None for n in value) else sum(value)


def main() -> None:
    print(solve([240, None]))


if __name__ == "__main__":
    main()
