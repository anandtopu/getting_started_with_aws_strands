"""Return missing setup steps in order: profile, budget, region; Ollama requires none of these.

Run: uv run python modules/00_setup/exercises/03_readiness.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return []


def main() -> None:
    print(solve({"provider": "bedrock", "profile": "nimbus", "region": "us-east-1"}))


if __name__ == "__main__":
    main()
