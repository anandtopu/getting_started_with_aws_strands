"""Fastapi sse: Nimbus Tier 3 lesson.

Run: uv run --group apps python modules/10_streaming/examples/03_fastapi_sse.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

import argparse

from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.web_apps import demonstrate, serve


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true")
    args, cfg = lesson_settings(parser)
    # KEY IDEA: replay tests the real ASGI routes; --serve starts the local browser app.
    if args.serve:
        serve(cfg)
    else:
        demonstrate(cfg)
        complete()


if __name__ == "__main__":
    run_cli(main)
