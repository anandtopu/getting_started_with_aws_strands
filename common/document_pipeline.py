"""Image extraction, deterministic validation and idempotent storage in a bounded Graph."""

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from strands.multiagent import GraphBuilder

from common.config import ROOT
from common.coordination import FunctionNode, worker
from common.data import data_path, load_jsonl
from common.testing import tool_message


class Document(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(pattern=r"^(RCP|INV)-\d{3}$")
    kind: Literal["receipt", "invoice"]
    subtotal_cents: int = Field(ge=0, strict=True)
    tax_cents: int = Field(ge=0, strict=True)
    total_cents: int = Field(ge=0, strict=True)
    currency: Literal["USD"] = "USD"


def flags(document):
    problems = []
    if document.subtotal_cents + document.tax_cents != document.total_cents:
        problems.append("total_mismatch")
    if document.total_cents > 50000:
        problems.append("supervisor_review")
    return problems


def store_sqlite(path: Path, fingerprint: str, document: Document, anomalies: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS documents "
            "(sha TEXT PRIMARY KEY, document TEXT, anomalies TEXT)"
        )
        changed = db.execute(
            "INSERT OR IGNORE INTO documents VALUES (?, ?, ?)",
            (fingerprint, document.model_dump_json(), json.dumps(anomalies)),
        ).rowcount
    return "stored" if changed else "duplicate"


def store_dynamo(client, table, fingerprint, document, anomalies):
    from botocore.exceptions import ClientError

    try:
        client.put_item(
            TableName=table,
            Item={
                "sha": {"S": fingerprint},
                "document": {"S": document.model_dump_json()},
                "anomalies": {"S": json.dumps(anomalies)},
            },
            ConditionExpression="attribute_not_exists(sha)",
        )
    except ClientError as error:
        if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return "duplicate"
        raise
    return "stored"


async def process_document(settings, relative: str, database: Path, *, dynamo=None, table=None):
    invoice_root = ROOT / "capstones/03_document_intelligence/fixtures"
    if relative.startswith("invoices/"):
        path = (invoice_root / relative).resolve()
        if not path.is_relative_to(invoice_root.resolve()):
            raise ValueError("Document must stay inside the course fixture directory")
    else:
        path = data_path(relative)
    if path.suffix.lower() != ".png" or path.stat().st_size > 2_000_000:
        raise ValueError("Choose a course PNG smaller than 2 MB")
    image = path.read_bytes()
    state = {"sha256": hashlib.sha256(image).hexdigest()}
    scripted = []
    if settings.provider == "mock":
        # Mock extraction is explicitly a fixture; it is not evidence of OCR accuracy.
        rows = load_jsonl("eval/receipts.jsonl") + [
            json.loads(line) for line in (invoice_root / "invoices.jsonl").read_text().splitlines()
        ]
        row = next(row for row in rows if row["file"] == relative)
        scripted = [
            tool_message(
                "Document",
                {
                    "document_id": row.get("receipt_id", row.get("invoice_id")),
                    "kind": "invoice" if "invoice_id" in row else "receipt",
                    **{k: row[k] for k in ("subtotal_cents", "tax_cents", "total_cents")},
                },
            )
        ]
    agent = worker(
        settings,
        "extract",
        scripted,
        structured_output_model=Document,
        prompt=(
            "Read only the supplied receipt or invoice image. Return its printed amounts "
            "in integer cents. Never fix a printed arithmetic error."
        ),
    )

    async def extract(task, invocation_state):
        result = await agent.invoke_async(
            [
                {"text": "Extract this document."},
                {"image": {"format": "png", "source": {"bytes": image}}},
            ],
            limits={"turns": 3},
        )
        state["document"] = result.structured_output
        return state["document"].model_dump()

    async def validate(task, invocation_state):
        state["anomalies"] = flags(state["document"])
        return {
            "anomalies": state["anomalies"],
            "route": "review" if state["anomalies"] else "accepted",
        }

    async def persist(task, invocation_state):
        arguments = (state["sha256"], state["document"], state["anomalies"])
        state["storage"] = (
            store_dynamo(dynamo, table, *arguments)
            if dynamo
            else store_sqlite(database, *arguments)
        )
        return {"storage": state["storage"]}

    builder = GraphBuilder()
    for name, function in (("extract", extract), ("validate", validate), ("store", persist)):
        builder.add_node(FunctionNode(name, function), name)
    builder.add_edge("extract", "validate")
    builder.add_edge("validate", "store")
    builder.set_entry_point("extract")
    builder.set_max_node_executions(3)
    builder.set_node_timeout(25)
    builder.set_execution_timeout(60)
    result = await builder.build().invoke_async("Process the selected image.")
    if "storage" not in state:
        raise ValueError("Document pipeline did not reach storage: " + str(result.status))
    state["document"] = state["document"].model_dump()
    state["extraction_scope"] = (
        "fixture, not OCR quality" if settings.provider == "mock" else "live vision extraction"
    )
    return state
