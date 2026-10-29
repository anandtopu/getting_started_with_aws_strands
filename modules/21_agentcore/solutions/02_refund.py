"""Allow only strict integer positive cents up to and including 50000.

Run: uv run python modules/21_agentcore/solutions/02_refund.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return type(value) is int and 0 < value <= 50000


def main() -> None:
    print(solve(1))


if __name__ == "__main__":
    main()
