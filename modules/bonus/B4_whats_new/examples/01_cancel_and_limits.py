"""Cancel an active bounded invocation.

Run: uv run --all-groups python modules/bonus/B4_whats_new/examples/01_cancel_and_limits.py --mock
Expected: checked result and Lesson complete. Mock cost $0; no AWS resources.
Live calls use configured provider prices; see this module's README."""

import asyncio

from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.release_lab import cancellation


def main() -> None:
    _, cfg = lesson_settings()
    # KEY IDEA: the helper runs the real SDK with explicit boundaries.
    print(asyncio.run(cancellation(cfg)))
    complete()


if __name__ == "__main__":
    run_cli(main)
