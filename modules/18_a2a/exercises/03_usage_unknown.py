"""Return unknown if any agent omits its usage; otherwise sum reported totals.

Run: uv run python modules/18_a2a/exercises/03_usage_unknown.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return sum(n or 0 for n in value)


def main() -> None:
    print(solve([240, None]))


if __name__ == "__main__":
    main()
