"""Trip Planner Crew reference solution.

Run: uv run --all-groups python capstones/02_trip_planner_crew/solution/main.py --mock
Expected: checked evidence and Lesson complete. Mock cost $0; see README for opt-in AWS."""

import argparse
import asyncio

from common.capstone_trip import plan_events
from common.config import ROOT
from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.trip_planning import TripRequest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget-cents", type=int, default=100000)
    args, cfg = lesson_settings(parser)
    directory = ROOT / ".nimbus/capstones/02_trip_planner_crew"
    directory.mkdir(parents=True, exist_ok=True)

    # KEY IDEA: evidence and authorization are enforced by the host below the model.
    async def run():
        async for event in plan_events(cfg, TripRequest(budget_cents=args.budget_cents)):
            print(event)

    asyncio.run(run())
    complete()


if __name__ == "__main__":
    run_cli(main)
