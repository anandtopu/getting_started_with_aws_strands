"""Accept only one nonempty string prompt no longer than 2000 characters.

Run: uv run python modules/20_deployment/exercises/02_payload.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return True


def main() -> None:
    print(solve({"prompt": "Refund time?"}))


if __name__ == "__main__":
    main()
