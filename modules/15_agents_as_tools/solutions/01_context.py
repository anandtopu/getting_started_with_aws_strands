"""Pass only city and nights to a hotel specialist; omit all private fields.

Run: uv run python modules/15_agents_as_tools/solutions/01_context.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return {k: value[k] for k in ("city", "nights")}


def main() -> None:
    print(solve({"city": "Porto", "nights": 2, "passport": "fake-private"}))


if __name__ == "__main__":
    main()
