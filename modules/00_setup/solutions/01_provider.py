"""Normalize a provider name and accept only the five supported live providers.

Run: uv run python modules/00_setup/solutions/01_provider.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return value.strip().lower() in {"bedrock", "ollama", "openai", "anthropic", "litellm"}


def main() -> None:
    print(solve(" OLLAMA "))


if __name__ == "__main__":
    main()
