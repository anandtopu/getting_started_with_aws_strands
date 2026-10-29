"""Accept only an explicit case-insensitive yes after stripping whitespace; missing input denies.

Run: uv run python modules/06_community_tools/solutions/03_consent.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return isinstance(value, str) and value.strip().lower() == "yes"


def main() -> None:
    print(solve(" YES "))


if __name__ == "__main__":
    main()
