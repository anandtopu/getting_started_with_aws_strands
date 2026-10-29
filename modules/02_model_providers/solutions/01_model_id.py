"""Use a nonempty explicit MODEL_ID; otherwise select the provider-specific ID.

Run: uv run python modules/02_model_providers/solutions/01_model_id.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return value.get("MODEL_ID") or value[value["MODEL_PROVIDER"].upper() + "_MODEL_ID"]


def main() -> None:
    print(solve({"MODEL_PROVIDER": "ollama", "MODEL_ID": "", "OLLAMA_MODEL_ID": "local"}))


if __name__ == "__main__":
    main()
