"""Return cosine similarity, including zero-vector behavior.

Run: uv run python modules/07_rag/solutions/02_cosine.py
Expected: sample output; check with the module exercise tests.
Cost/resources: local Python only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: check the complete contract, including rejection cases.
    from common.retrieval import cosine

    return round(cosine(value[0], value[1]), 6)


def main() -> None:
    print(solve([[1, 0], [1, 0]]))


if __name__ == "__main__":
    main()
