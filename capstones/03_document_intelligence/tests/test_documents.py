"""Image pipeline validation, retention of anomalies, and conditional DynamoDB writes."""

import json
from pathlib import Path

import boto3
import pytest
from moto import mock_aws

from common.config import load_settings
from common.document_pipeline import Document, process_document, store_dynamo


@pytest.mark.parametrize(
    "case", json.loads((Path(__file__).parents[1] / "evaluation.json").read_text())
)
async def test_images_and_retry(case, tmp_path):
    cfg = load_settings(provider="mock")
    report = await process_document(cfg, case["file"], tmp_path / "documents.db")
    assert report["anomalies"] == case["anomalies"]
    assert report["storage"] == "stored"
    assert (await process_document(cfg, case["file"], tmp_path / "documents.db"))[
        "storage"
    ] == "duplicate"


def test_dynamodb_conditional_write():
    with mock_aws():
        api = boto3.client(
            "dynamodb",
            region_name="us-east-1",
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
        )
        api.create_table(
            TableName="documents",
            KeySchema=[{"AttributeName": "sha", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "sha", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        document = Document(
            document_id="INV-001", kind="invoice", subtotal_cents=100, tax_cents=10, total_cents=110
        )
        assert store_dynamo(api, "documents", "abc", document, []) == "stored"
        assert store_dynamo(api, "documents", "abc", document, []) == "duplicate"
        assert "document" in api.get_item(TableName="documents", Key={"sha": {"S": "abc"}})["Item"]
