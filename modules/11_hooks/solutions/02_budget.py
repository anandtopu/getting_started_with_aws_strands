"""Allow only catalog-priced destinations inside the trusted budget.

Run: uv run python modules/11_hooks/solutions/02_budget.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    price = {"BOS": 35000, "LAX": 90000}.get(value["destination"].strip().upper())
    return price is not None and price <= value["budget"]


def main():
    print(solve({"destination": " bos ", "budget": 35000}))


if __name__ == "__main__":
    main()
