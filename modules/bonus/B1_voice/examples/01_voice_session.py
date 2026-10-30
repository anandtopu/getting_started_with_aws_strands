"""A bounded BidiAgent connection.

Run: uv run --all-groups python modules/bonus/B1_voice/examples/01_voice_session.py --mock
Expected: checked result and Lesson complete. Mock cost $0; no AWS resources.
Live calls use configured provider prices; see this module's README."""

import asyncio

from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.voice_lab import voice_session


def main() -> None:
    _, cfg = lesson_settings()
    # KEY IDEA: the helper runs the real SDK with explicit boundaries.
    print(asyncio.run(voice_session(cfg)))
    complete()


if __name__ == "__main__":
    run_cli(main)
