"""Extract only public text deltas; never leak tool inputs or raw trace metadata.

Run: uv run python modules/10_streaming/exercises/02_text_only.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return value


def main():
    print(solve([{"data": "Hi"}, {"metadata": {"secret": "x"}}, {"data": " there"}]))


if __name__ == "__main__":
    main()
