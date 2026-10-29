"""Accept only a streaming card whose exact URL is in the host allow-list.

Run: uv run python modules/18_a2a/exercises/01_card.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return True


def main() -> None:
    print(
        solve(
            {
                "card": {"url": "https://partner.example/", "capabilities": {"streaming": True}},
                "allowed": ["https://partner.example/"],
            }
        )
    )


if __name__ == "__main__":
    main()
