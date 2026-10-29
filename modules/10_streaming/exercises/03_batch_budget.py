"""Split jobs into ordered batches no larger than the positive worker budget.

Run: uv run python modules/10_streaming/exercises/03_batch_budget.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return [value["jobs"]]


def main():
    print(solve({"jobs": [1, 2, 3, 4, 5], "workers": 2}))


if __name__ == "__main__":
    main()
