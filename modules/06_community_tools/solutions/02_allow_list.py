"""Approve only an exact GET to WEATHER_URL; reject writes and alternate URLs.

Run: uv run python modules/06_community_tools/solutions/02_allow_list.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    from common.tools.travel_day import WEATHER_URL

    return value["method"] == "GET" and value["url"] == WEATHER_URL


def main() -> None:
    print(solve({"method": "GET", "url": "https://example.com"}))


if __name__ == "__main__":
    main()
