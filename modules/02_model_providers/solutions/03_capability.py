"""Enable the Nova low-effort settings only when the model ID contains nova-2-lite.

Run: uv run python modules/02_model_providers/solutions/03_capability.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return (
        {"reasoningConfig": {"type": "enabled", "maxReasoningEffort": "low"}}
        if "nova-2-lite" in value
        else {}
    )


def main() -> None:
    print(solve("us.amazon.nova-2-lite-v1:0"))


if __name__ == "__main__":
    main()
