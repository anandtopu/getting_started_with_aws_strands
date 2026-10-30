"""Inspect the actual document stack's lifecycle and IAM scope."""

import json
import runpy

import pytest

from common.config import ROOT


def test_document_stack_is_disposable_and_table_scoped(tmp_path, monkeypatch):
    pytest.importorskip("aws_cdk")
    monkeypatch.setenv("CDK_OUTDIR", str(tmp_path))
    runpy.run_path(str(ROOT / "infra/document_pipeline/app.py"))
    template = json.loads((tmp_path / "NimbusDocuments.template.json").read_text())
    resources = template["Resources"]
    name, table = next(
        (name, resource)
        for name, resource in resources.items()
        if resource["Type"] == "AWS::DynamoDB::Table"
    )
    assert table["DeletionPolicy"] == "Delete"
    assert table["Properties"]["BillingMode"] == "PAY_PER_REQUEST"
    assert {"Key": "project", "Value": "getting-started-with-aws-strands"} in table["Properties"][
        "Tags"
    ]
    policy = next(r for r in resources.values() if r["Type"] == "AWS::IAM::ManagedPolicy")
    statement = policy["Properties"]["PolicyDocument"]["Statement"][0]
    assert set(statement["Action"]) == {"dynamodb:PutItem", "dynamodb:GetItem"}
    assert statement["Resource"] == {"Fn::GetAtt": [name, "Arn"]}
