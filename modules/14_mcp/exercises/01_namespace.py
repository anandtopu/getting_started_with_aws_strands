"""Prefix tool names with the reviewed server name, preserving order.

Run: uv run python modules/14_mcp/exercises/01_namespace.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return value["tools"]


def main():
    print(solve({"server": "nimbus", "tools": ["search", "book"]}))


if __name__ == "__main__":
    main()
