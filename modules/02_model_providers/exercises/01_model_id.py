"""Use a nonempty explicit MODEL_ID; otherwise select the provider-specific ID.

Run: uv run python modules/02_model_providers/exercises/01_model_id.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE: replace this runnable baseline to satisfy the stated contract.
    return value.get("MODEL_ID", "")


def main() -> None:
    result = solve({"MODEL_PROVIDER": "ollama", "MODEL_ID": "", "OLLAMA_MODEL_ID": "local"})
    print("Selected ID:", repr(result))


if __name__ == "__main__":
    main()
