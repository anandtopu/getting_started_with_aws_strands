"""use_aws with scoped read-only role; denied write demonstration.

Run: uv run python modules/06_community_tools/examples/05_read_only_aws.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: Yes; recorded contract locally. Resources created: none.
"""

from contextlib import nullcontext
from unittest.mock import patch

import boto3
from botocore.stub import Stubber
from strands import Agent
from strands_tools import use_aws

from common.config import load_settings
from common.lessons import complete, lesson_settings, require_bedrock
from common.models import get_model
from common.pretty import console, run_cli


def guarded_call(agent, operation: str, region: str, profile: str) -> dict:
    # KEY IDEA: reject writes before delegating; IAM is a separate enforcement layer.
    if operation != "describe_regions":
        raise PermissionError("Only ec2.describe_regions is allowed")
    return agent.tool.use_aws(
        service_name="ec2",
        operation_name=operation,
        parameters={},
        region=region,
        profile_name=profile,
        label="Read region names",
    )


def main() -> None:
    args, cfg = lesson_settings()
    agent = Agent(
        model=get_model(cfg, responses=[] if args.mock else None),
        tools=[use_aws],
        callback_handler=None,
    )
    target = load_settings(provider="bedrock")
    if args.mock:
        client = boto3.client(
            "ec2",
            region_name=target.aws_region,
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
        )
        stub = Stubber(client)
        stub.add_response("describe_regions", {"Regions": [{"RegionName": "us-east-1"}]}, {})
        context = patch.object(use_aws, "get_boto3_client", return_value=client)
    else:
        require_bedrock(cfg)
        context, stub = nullcontext(), nullcontext()
    with context, stub:
        console.print(
            guarded_call(agent, "describe_regions", target.aws_region, target.aws_profile)
        )
        try:
            guarded_call(agent, "terminate_instances", target.aws_region, target.aws_profile)
        except PermissionError as exc:
            console.print("Write denied:", str(exc))
    complete()


if __name__ == "__main__":
    run_cli(main)
