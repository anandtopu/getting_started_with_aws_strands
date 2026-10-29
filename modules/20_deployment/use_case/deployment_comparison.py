"""Compare identical support code on Lambda and Runtime: Nimbus production lesson.

Run: uv run --all-groups python modules/20_deployment/use_case/deployment_comparison.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

import argparse
import asyncio

from common.config import course_value
from common.deployment_apps import compare_local
from common.deployment_calls import invoke_lambda, invoke_runtime
from common.lessons import complete, lesson_settings
from common.pretty import run_cli


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live-aws", action="store_true")
    args, cfg = lesson_settings(parser)
    if args.live_aws and args.mock:
        parser.error("Choose local --mock or --live-aws, not both")
    if args.live_aws:
        print("Lambda:", invoke_lambda(cfg, course_value("NIMBUS_LAMBDA_NAME")))
        print("Runtime:", invoke_runtime(cfg, course_value("AGENTCORE_RUNTIME_ARN")))
    else:
        print(asyncio.run(compare_local(cfg)))
    print("Repeat warm live measurements; include billed duration, tokens and idle resources.")
    complete()


if __name__ == "__main__":
    run_cli(main)
