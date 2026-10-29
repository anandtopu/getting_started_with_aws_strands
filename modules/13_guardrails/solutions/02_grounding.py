"""Require a known source and an exact nonempty quote before displaying a citation.

Run: uv run python modules/13_guardrails/solutions/02_grounding.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return bool(value["quote"]) and value["quote"] in value["sources"].get(value["source"], "")


def main():
    print(solve({"quote": "5 days", "source": "policy", "sources": {"policy": "Wait 5 days"}}))


if __name__ == "__main__":
    main()
