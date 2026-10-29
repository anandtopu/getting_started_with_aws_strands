"""Accept a quote only when its chunk ID, source, page and text match retrieved evidence.

Run: uv run python modules/07_rag/solutions/03_citations.py
Expected: sample output; check with the module exercise tests.
Cost/resources: local Python only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: check the complete contract, including rejection cases.
    return any(
        c["id"] == value["id"]
        and c["source"] == value["source"]
        and c["page"] == value["page"]
        and value["quote"]
        and value["quote"] in c["text"]
        for c in value["evidence"]
    )


def main() -> None:
    print(
        solve(
            {
                "id": "a",
                "source": "refund.md",
                "page": 3,
                "quote": "5 days",
                "evidence": [{"id": "a", "source": "refund.md", "page": 3, "text": "Wait 5 days"}],
            }
        )
    )


if __name__ == "__main__":
    main()
