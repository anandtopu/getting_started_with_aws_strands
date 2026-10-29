"""Approve only an exact GET to WEATHER_URL; reject writes and alternate URLs.

Run: uv run python modules/06_community_tools/exercises/02_allow_list.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return value["method"] == "GET"


def main() -> None:
    print(solve({"method": "GET", "url": "https://example.com"}))


if __name__ == "__main__":
    main()
