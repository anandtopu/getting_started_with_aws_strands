"""Use the checked convert_budget tool and return its displayed conversion.

Run: uv run python modules/06_community_tools/solutions/01_budget.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    from common.tools.travel_day import convert_budget

    return convert_budget(value["amount"], value["rate"])


def main() -> None:
    print(solve({"amount": "100", "rate": ".92"}))


if __name__ == "__main__":
    main()
