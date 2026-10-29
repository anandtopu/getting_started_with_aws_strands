"""Inspect, upload synthetic policies or remove one tagged, explicitly selected lab.

Run: uv run python scripts/tier2_lab.py NimbusKnowledgeLab inspect
Read-only by default; mutation requires --execute --confirm-stack NAME.
Cost/resources: optional lab storage and ingestion charges; see infra/README.md.
"""

import argparse
import json

from common.aws_retrieval import aws_client
from common.data import data_path
from common.pretty import console, run_cli

STACKS = {"NimbusKnowledgeLab", "NimbusSessionLab", "NimbusMemoryLab", "NimbusGuardrailLab"}
PROJECT = "getting-started-with-aws-strands"


def checked_stack(client, name: str) -> dict:
    if name not in STACKS:
        raise ValueError("Choose one of the named course lab stacks")
    stack = client.describe_stacks(StackName=name)["Stacks"][0]
    if {t["Key"]: t["Value"] for t in stack.get("Tags", [])}.get("project") != PROJECT:
        raise PermissionError("Stack is not tagged as this course's lab")
    return stack


def empty_bucket(client, name: str) -> None:
    """Only called with physical bucket IDs from the verified stack resource inventory."""
    # These lab buckets intentionally have versioning disabled. Refuse unexpected versioning.
    if client.get_bucket_versioning(Bucket=name).get("Status"):
        raise ValueError("Versioned bucket requires separate reviewed version cleanup")
    for page in client.get_paginator("list_objects_v2").paginate(Bucket=name):
        objects = [{"Key": item["Key"]} for item in page.get("Contents", [])]
        if objects:
            response = client.delete_objects(Bucket=name, Delete={"Objects": objects})
            if response.get("Errors"):
                raise RuntimeError("Some objects could not be deleted; stack deletion stopped")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stack", choices=sorted(STACKS))
    parser.add_argument("action", choices=["inspect", "ingest", "destroy"])
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm-stack")
    args = parser.parse_args()
    cloud = aws_client("cloudformation", mock=False)
    stack = checked_stack(cloud, args.stack)
    outputs = {item["OutputKey"]: item["OutputValue"] for item in stack.get("Outputs", [])}
    resources = [
        item
        for page in cloud.get_paginator("list_stack_resources").paginate(StackName=args.stack)
        for item in page["StackResourceSummaries"]
    ]
    console.print(
        {
            "stack": args.stack,
            "action": args.action,
            "outputs": outputs,
            "resources": [
                {"type": r["ResourceType"], "id": r.get("PhysicalResourceId")} for r in resources
            ],
        }
    )
    if args.action == "inspect" or not args.execute:
        console.print("Read-only inspection. No changes made.")
        return
    if args.confirm_stack != args.stack:
        raise PermissionError("Mutation requires --confirm-stack with the exact displayed name")
    s3 = aws_client("s3", mock=False)
    if args.action == "ingest":
        if args.stack != "NimbusKnowledgeLab":
            raise ValueError("Only the Knowledge lab supports ingestion")
        for path in sorted(data_path("policies/refund.md").parent.glob("*.md")):
            key = f"policies/{path.name}"
            s3.put_object(Bucket=outputs["DocumentsBucket"], Key=key, Body=path.read_bytes())
            s3.put_object(
                Bucket=outputs["DocumentsBucket"],
                Key=key + ".metadata.json",
                Body=json.dumps({"metadataAttributes": {"topic": path.stem}}).encode(),
            )
        result = aws_client("bedrock-agent", mock=False).start_ingestion_job(
            knowledgeBaseId=outputs["KnowledgeBaseId"], dataSourceId=outputs["DataSourceId"]
        )
        console.print(
            "Ingestion started; wait for COMPLETE before querying:",
            result["ingestionJob"]["ingestionJobId"],
        )
    else:
        for resource in resources:
            if resource["ResourceType"] == "AWS::S3::Bucket":
                empty_bucket(s3, resource["PhysicalResourceId"])
        cloud.delete_stack(StackName=args.stack)
        cloud.get_waiter("stack_delete_complete").wait(StackName=args.stack)
        console.print(
            "Stack deletion complete. Run scripts/find_leftovers.py for the configured region."
        )


if __name__ == "__main__":
    run_cli(main)
