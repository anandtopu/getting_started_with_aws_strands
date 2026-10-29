"""Require a known source and an exact nonempty quote before displaying a citation.

Run: uv run python modules/13_guardrails/exercises/02_grounding.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return True


def main():
    print(solve({"quote": "5 days", "source": "policy", "sources": {"policy": "Wait 5 days"}}))


if __name__ == "__main__":
    main()
