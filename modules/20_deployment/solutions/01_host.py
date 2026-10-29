"""Choose local, then managed sessions, then streaming/over-900s Fargate, otherwise Lambda.

Run: uv run python modules/20_deployment/solutions/01_host.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return (
        "local"
        if value["local"]
        else "AgentCore Runtime"
        if value["sessions"]
        else "Fargate"
        if value["streaming"] or value["seconds"] > 900
        else "Lambda"
    )


def main() -> None:
    print(solve({"local": True, "sessions": False, "streaming": False, "seconds": 5}))


if __name__ == "__main__":
    main()
