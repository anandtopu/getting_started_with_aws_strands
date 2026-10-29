"""Allow the budget node only when flight and hotel are both completed.

Run: uv run python modules/17_graphs/solutions/01_join.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return all(value.get(name) == "completed" for name in ("flight", "hotel"))


def main() -> None:
    print(solve({"flight": "completed", "hotel": "completed"}))


if __name__ == "__main__":
    main()
