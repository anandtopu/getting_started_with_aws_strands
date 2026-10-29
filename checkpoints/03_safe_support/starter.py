"""Runnable starter for the streaming, approved, guarded MCP support checkpoint.

Run: uv run python checkpoints/03_safe_support/starter.py --mock
Cost/resources: $0; this starter performs no actions.
"""

from common.lessons import complete, lesson_settings


def support_contract():
    # YOUR CODE HERE: compose local MCP, streaming, policy hooks and durable approval.
    return {"status": "not_implemented", "audit": []}


def main():
    lesson_settings()
    print(support_contract())
    complete()


if __name__ == "__main__":
    main()
