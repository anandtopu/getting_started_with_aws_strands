"""Authenticated FastAPI SSE adapter: Nimbus production lesson.

Run: uv run --all-groups python modules/20_deployment/examples/05_fargate_api.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

import asyncio

from common.deployment_apps import compare_local
from common.lessons import complete, lesson_settings
from common.pretty import run_cli


def main() -> None:
    _, cfg = lesson_settings()
    # KEY IDEA: these are actual ASGI requests to the two app adapters, not AWS latency tests.
    print(asyncio.run(compare_local(cfg)))
    complete()


if __name__ == "__main__":
    run_cli(main)
