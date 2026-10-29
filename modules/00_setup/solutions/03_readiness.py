"""Return missing setup steps in order: profile, budget, region; Ollama requires none of these.

Run: uv run python modules/00_setup/solutions/03_readiness.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return (
        []
        if value["provider"] == "ollama"
        else [key for key in ("profile", "budget", "region") if not value.get(key)]
    )


def main() -> None:
    print(solve({"provider": "bedrock", "profile": "nimbus", "region": "us-east-1"}))


if __name__ == "__main__":
    main()
