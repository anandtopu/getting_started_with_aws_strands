"""Encode one SSE text frame without allowing a newline to forge another event.

Run: uv run python modules/10_streaming/solutions/01_frame.py
Expected: sample output; check with the module exercise tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    from common.streaming import sse

    return sse("text", {"text": value})


def main():
    print(solve("hello"))


if __name__ == "__main__":
    main()
