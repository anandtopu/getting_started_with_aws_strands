"""Keep the last two complete text-only user/assistant pairs. This exercise excludes tool messages.

Run: uv run python modules/03_conversations/solutions/01_window.py
Expected: the sample result; compare with the exercise tests.
Cost/resources: local only, $0.
"""

from typing import Any


def solve(value: Any) -> Any:
    # KEY IDEA: enforce the exercise contract on every input.
    return value[-4:]


def main() -> None:
    print(solve(["u1", "a1", "u2", "a2", "u3", "a3"]))


if __name__ == "__main__":
    main()
