"""Enable the Nova low-effort settings only when the model ID contains nova-2-lite.

Run: uv run python modules/02_model_providers/exercises/03_capability.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return {}


def main() -> None:
    print(solve("us.amazon.nova-2-lite-v1:0"))


if __name__ == "__main__":
    main()
