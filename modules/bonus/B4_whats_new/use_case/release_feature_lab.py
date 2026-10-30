"""Pinned-release feature lab use case.

Run: uv run --all-groups python modules/bonus/B4_whats_new/use_case/release_feature_lab.py --mock
Expected: checked result and Lesson complete. Mock cost $0; no AWS resources.
Live calls use configured provider prices; see this module's README."""

import asyncio

from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.release_lab import middleware, redteam


def main() -> None:
    _, cfg = lesson_settings()
    # KEY IDEA: the helper runs the real SDK with explicit boundaries.
    print(asyncio.run(middleware(cfg)))
    print(asyncio.run(redteam(cfg)))
    complete()


if __name__ == "__main__":
    run_cli(main)
