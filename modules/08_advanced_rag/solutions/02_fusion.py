"""Fuse two ranked ID lists with reciprocal rank weights 1/(60+rank), deduplicating IDs.

Run: uv run python modules/08_advanced_rag/solutions/02_fusion.py
Expected: sample output; check with the module exercise tests.
Cost/resources: local Python only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: check the complete contract, including rejection cases.
    scores = {}
    for order in value:
        for rank, ident in enumerate(dict.fromkeys(order), 1):
            scores[ident] = scores.get(ident, 0) + 1 / (60 + rank)
    return sorted(scores, key=lambda ident: (-scores[ident], ident))


def main() -> None:
    print(solve([["a", "b"], ["b", "c"]]))


if __name__ == "__main__":
    main()
