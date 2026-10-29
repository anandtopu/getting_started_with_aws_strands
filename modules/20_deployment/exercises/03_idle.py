"""Sum hourly task, ALB and IPv4 rates, then multiply by hours.

Run: uv run python modules/20_deployment/exercises/03_idle.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return value["task"] * value["hours"]


def main() -> None:
    print(solve({"task": 0.01, "alb": 0.02, "ip_count": 3, "ip_rate": 0.005, "hours": 10}))


if __name__ == "__main__":
    main()
