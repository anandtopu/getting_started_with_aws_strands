"""Compute source hit rate; exclude abstention cases without an expected source.

Run: uv run python modules/08_advanced_rag/solutions/03_hit_rate.py
Expected: sample output; check with the module exercise tests.
Cost/resources: local Python only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: check the complete contract, including rejection cases.
    scored = [r for r in value if r.get("expected_source")]
    return (
        sum(r["expected_source"] in r["retrieved_sources"] for r in scored) / len(scored)
        if scored
        else 0.0
    )


def main() -> None:
    print(
        solve(
            [
                {"expected_source": "a", "retrieved_sources": ["a"]},
                {"expected_source": "b", "retrieved_sources": ["a"]},
                {"retrieved_sources": []},
            ]
        )
    )


if __name__ == "__main__":
    main()
