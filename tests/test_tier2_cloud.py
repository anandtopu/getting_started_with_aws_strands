"""Exact AWS request contracts and synthesized resource/IAM boundaries, no account."""

import asyncio
import json

import pytest

from common.aws_retrieval import bedrock_rerank, knowledge_store, titan_vector


def test_bedrock_contracts():
    with knowledge_store(True) as store:
        result = asyncio.run(store.search("refund timing"))
        assert "business days" in result[0].content
    assert len(titan_vector("refund", mock=True)) == 256
    assert bedrock_rerank("refund", ["refund timing", "seat"], mock=True)[0]["index"] == 0


def test_optional_cdk_resources_and_permissions(tmp_path):
    cdk = pytest.importorskip("aws_cdk")
    from aws_cdk.assertions import Template

    from common.infra_stacks import KnowledgeStack, MemoryStack, SessionStack

    for cls, name in [
        (KnowledgeStack, "Knowledge"),
        (SessionStack, "Sessions"),
        (MemoryStack, "Memory"),
    ]:
        app = cdk.App(outdir=str(tmp_path / name))
        stack = cls(app, name, env=cdk.Environment(account="111122223333", region="us-east-1"))
        template = Template.from_stack(stack).to_json()
        assert template["Resources"]
        for resource in template["Resources"].values():
            props = resource.get("Properties", {})
            if resource["Type"] == "AWS::S3::Bucket":
                assert all(props["PublicAccessBlockConfiguration"].values())
                assert props["BucketEncryption"]
            for document in [
                props.get("PolicyDocument", {}),
                *[p["PolicyDocument"] for p in props.get("Policies", [])],
            ]:
                for statement in document.get("Statement", []):
                    actions = statement["Action"]
                    assert not any(
                        "*" in a for a in ([actions] if isinstance(actions, str) else actions)
                    )
        (tmp_path / f"{name}.json").write_text(json.dumps(template))
        app.synth()


def test_cleanup_rejects_unowned_stacks_and_removes_only_selected_bucket():
    import boto3
    from moto import mock_aws

    from scripts.tier2_lab import checked_stack, empty_bucket

    class WrongProject:
        def describe_stacks(self, **kwargs):
            return {"Stacks": [{"Tags": [{"Key": "project", "Value": "another-project"}]}]}

    with pytest.raises(PermissionError):
        checked_stack(WrongProject(), "NimbusKnowledgeLab")
    with pytest.raises(ValueError):
        checked_stack(WrongProject(), "UnrelatedStack")
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        for name in ("nimbus-selected", "nimbus-preserved"):
            s3.create_bucket(Bucket=name)
            s3.put_object(Bucket=name, Key="demo", Body=b"synthetic")
        empty_bucket(s3, "nimbus-selected")
        assert s3.list_objects_v2(Bucket="nimbus-selected")["KeyCount"] == 0
        assert s3.list_objects_v2(Bucket="nimbus-preserved")["KeyCount"] == 1
