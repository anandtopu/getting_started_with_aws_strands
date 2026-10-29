"""Return None for unpriced hosted inference and zero for Ollama/mock.

Run: uv run python modules/02_model_providers/exercises/02_price.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return 0.0


def main() -> None:
    print(solve({"provider": "bedrock"}))


if __name__ == "__main__":
    main()
