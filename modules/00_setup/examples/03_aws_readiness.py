"""Identity Center, CLI v2 SSO, budget-before-billing gate, region and model-access checks.

Run: uv run python modules/00_setup/examples/03_aws_readiness.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: Yes; local readiness instead. Resources created: none.
"""

import argparse

from common.lessons import complete, lesson_settings, require_bedrock
from common.pretty import console, run_cli
from scripts.check_env import check_aws


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-account", action="store_true")
    args, cfg = lesson_settings(parser)
    console.print("SSO -> named profile -> budget -> region/model access -> inference.")
    # KEY IDEA: the default explains readiness without contacting an AWS account.
    if args.check_account and not args.mock:
        require_bedrock(cfg)
        check_aws(cfg)
    else:
        console.print("Read docs/AWS_SETUP.md; no identity or model access has been verified.")
    complete()


if __name__ == "__main__":
    run_cli(main)
