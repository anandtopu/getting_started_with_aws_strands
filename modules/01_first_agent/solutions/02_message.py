"""Concatenate only text content blocks from an assistant message.

Run: uv run python modules/01_first_agent/solutions/02_message.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return "".join(block["text"] for block in value["content"] if "text" in block)


def main() -> None:
    print(solve({"content": [{"text": "Hello "}, {"toolUse": {}}, {"text": "Nimbus"}]}))


if __name__ == "__main__":
    main()
