"""Build an audit record that omits raw arguments and redacts status text.

Run: uv run python modules/11_hooks/exercises/03_audit.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # YOUR CODE HERE
    return value


def main():
    print(solve({"name": "quote", "status": "ok", "arguments": {"email": "a@example.com"}}))


if __name__ == "__main__":
    main()
