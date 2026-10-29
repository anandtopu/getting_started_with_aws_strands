"""Split words into overlapping windows; reject non-progressing settings.

Run: uv run python modules/07_rag/solutions/01_chunks.py
Expected: sample output; check with the module exercise tests.
Cost/resources: local Python only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: check the complete contract, including rejection cases.
    from common.retrieval import split_text

    return split_text(value["text"], value["size"], value["overlap"])


def main() -> None:
    print(solve({"text": "one two three four five", "size": 3, "overlap": 1}))


if __name__ == "__main__":
    main()
