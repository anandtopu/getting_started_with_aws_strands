"""Eaming trip planner: Nimbus Tier 3 lesson.

Run: uv run python modules/10_streaming/use_case/streaming_trip_planner.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

import argparse
import asyncio

from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.streaming import planner, public_stream


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true")
    args, cfg = lesson_settings(parser)
    if args.serve:
        from common.web_apps import serve

        serve(cfg)
    else:

        async def replay():
            async for frame in public_stream(planner(cfg), "Plan a Boston weekend"):
                print(frame, end="")

        asyncio.run(replay())
        complete()


if __name__ == "__main__":
    run_cli(main)
