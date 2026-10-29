"""Build an audit record that omits raw arguments and redacts status text.

Run: uv run python modules/11_hooks/solutions/03_audit.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    from common.audit import redact

    return {"name": value["name"], "status": redact(value["status"])}


def main():
    print(solve({"name": "quote", "status": "ok", "arguments": {"email": "a@example.com"}}))


if __name__ == "__main__":
    main()
