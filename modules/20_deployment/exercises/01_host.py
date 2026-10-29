"""Choose local, then managed sessions, then streaming/over-900s Fargate, otherwise Lambda.

Run: uv run python modules/20_deployment/exercises/01_host.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return "Lambda"


def main() -> None:
    print(solve({"local": True, "sessions": False, "streaming": False, "seconds": 5}))


if __name__ == "__main__":
    main()
