"""Route to review only when the authoritative subtotal fits the budget.

Run: uv run python modules/17_graphs/exercises/02_route.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return "review"


def main() -> None:
    print(solve({"cents": [35600, 17200], "budget": 52800}))


if __name__ == "__main__":
    main()
