"""Nimbus Support Copilot reference solution.

Run: uv run --all-groups python capstones/04_nimbus_support_copilot/solution/main.py --mock
Expected: checked evidence and Lesson complete. Mock cost $0; see README for opt-in AWS."""

import argparse
import asyncio

from common.config import ROOT
from common.flagship import cloud_support, local_support, release_report
from common.lessons import complete, lesson_settings
from common.pretty import run_cli


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live-aws", action="store_true")
    parser.add_argument("--guarded", action="store_true")
    parser.add_argument("--trace", action="store_true")
    args, cfg = lesson_settings(parser)
    directory = ROOT / ".nimbus/capstones/04_nimbus_support_copilot"
    directory.mkdir(parents=True, exist_ok=True)
    # KEY IDEA: evidence and authorization are enforced by the host below the model.
    if args.live_aws:
        if args.mock:
            raise ValueError("Choose mock or live AWS, not both")
        print(asyncio.run(cloud_support(cfg)))
    elif args.guarded:
        print(asyncio.run(local_support(cfg, directory, guarded=True)))
    elif args.trace:
        from common.telemetry_lab import local_otlp_receiver, trace_run

        async def workload():
            result = await release_report(cfg, directory)
            return {"usage": result["support"]["policy"]["usage"]}

        with local_otlp_receiver() as (endpoint, batches):
            print(trace_run(cfg, endpoint=endpoint, workload=workload))
            print({"otlp_batches": len(batches)})
    else:
        print(asyncio.run(release_report(cfg, directory)))
    complete()


if __name__ == "__main__":
    run_cli(main)
