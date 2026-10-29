"""Return None for unpriced hosted inference and zero for Ollama/mock.

Run: uv run python modules/02_model_providers/solutions/02_price.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return 0.0 if value["provider"] in {"ollama", "mock"} else value.get("known_cost")


def main() -> None:
    print(solve({"provider": "bedrock"}))


if __name__ == "__main__":
    main()
