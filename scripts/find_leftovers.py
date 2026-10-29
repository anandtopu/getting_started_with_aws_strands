"""Read-only regional inventory of tagged course resources and stack children.

Run: uv run python scripts/find_leftovers.py --regions us-east-1
Cost: no resources created; AWS API usage may be metered. Requires SSO.
An empty result is NOT proof that untagged resources or unscanned services are gone.
"""

import argparse
import json
from typing import Any

import boto3
from botocore.config import Config

from common.config import load_settings
from common.pretty import friendly_error, run_cli

TAG_KEY = "project"
TAG_VALUE = "getting-started-with-aws-strands"


def scan_region(tagging: Any, cloudformation: Any, region: str) -> dict[str, Any]:
    resources: dict[str, dict[str, Any]] = {}
    errors = []
    try:
        pages = tagging.get_paginator("get_resources").paginate(
            TagFilters=[{"Key": TAG_KEY, "Values": [TAG_VALUE]}]
        )
        for page in pages:
            for row in page["ResourceTagMappingList"]:
                resources[row["ResourceARN"]] = {
                    "id": row["ResourceARN"],
                    "source": "tagging",
                    "region": region,
                }
    except Exception as exc:
        errors.append({"service": "tagging", "message": friendly_error(exc)})
    try:
        for page in cloudformation.get_paginator("describe_stacks").paginate():
            for stack in page["Stacks"]:
                if not any(
                    t["Key"] == TAG_KEY and t["Value"] == TAG_VALUE for t in stack.get("Tags", [])
                ):
                    continue
                if stack["StackStatus"] == "DELETE_COMPLETE":
                    continue
                stack_id = stack["StackId"]
                resources[stack_id] = {"id": stack_id, "source": "cloudformation", "region": region}
                for children in cloudformation.get_paginator("list_stack_resources").paginate(
                    StackName=stack_id
                ):
                    for child in children["StackResourceSummaries"]:
                        if child["ResourceStatus"] != "DELETE_COMPLETE":
                            key = child.get("PhysicalResourceId", child["LogicalResourceId"])
                            resources[key] = {
                                "id": key,
                                "type": child["ResourceType"],
                                "stack": stack_id,
                                "source": "stack child",
                                "region": region,
                            }
    except Exception as exc:
        errors.append({"service": "cloudformation", "message": friendly_error(exc)})
    return {
        "region": region,
        "resources": sorted(resources.values(), key=lambda x: x["id"]),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--regions", nargs="+", required=True, help="Explicitly list every region used"
    )
    parser.add_argument("--profile", help="Override the named SSO profile")
    args = parser.parse_args()
    settings = load_settings()
    session = boto3.Session(profile_name=args.profile or settings.aws_profile or None)
    reports = []
    config = Config(connect_timeout=5, read_timeout=20, retries={"max_attempts": 2})
    for region in dict.fromkeys(args.regions):
        try:
            reports.append(
                scan_region(
                    session.client("resourcegroupstaggingapi", region_name=region, config=config),
                    session.client("cloudformation", region_name=region, config=config),
                    region,
                )
            )
        except Exception as exc:
            reports.append(
                {"region": region, "resources": [], "errors": [{"message": friendly_error(exc)}]}
            )
    print(
        json.dumps(
            {
                "scans": reports,
                "scope": "Resource Groups Tagging API and active tagged CloudFormation stacks",
                "limitations": [
                    "Untagged resources and unsupported services are not covered.",
                    "Deleted stacks may retain assets; check the lesson's inventory.",
                    "Check global resources, budgets, sessions and unlisted regions separately.",
                    "Service-specific scanners will accompany their infrastructure lessons.",
                ],
                "conclusion": "No claim of an empty AWS account is made by this scan.",
            },
            indent=2,
        )
    )
    if any(r["errors"] for r in reports):
        return 2
    return 1 if any(r["resources"] for r in reports) else 0


if __name__ == "__main__":
    run_cli(main)
