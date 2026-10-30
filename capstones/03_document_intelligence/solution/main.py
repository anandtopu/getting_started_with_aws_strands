"""Document Intelligence Pipeline reference solution.

Run: uv run --all-groups python capstones/03_document_intelligence/solution/main.py --mock
Expected: checked evidence and Lesson complete. Mock cost $0; see README for opt-in AWS."""

import argparse
import asyncio

from common.cloud_clients import client
from common.config import ROOT, course_value
from common.document_pipeline import process_document
from common.lessons import complete, lesson_settings
from common.pretty import run_cli


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="invoices/invoice_02.png")
    parser.add_argument("--dynamodb", action="store_true")
    args, cfg = lesson_settings(parser)
    directory = ROOT / ".nimbus/capstones/03_document_intelligence"
    directory.mkdir(parents=True, exist_ok=True)
    # KEY IDEA: evidence and authorization are enforced by the host below the model.
    api = None
    table = course_value("NIMBUS_DOCUMENT_TABLE")
    if args.dynamodb:
        if args.mock or not table:
            raise ValueError("Live DynamoDB requires NIMBUS_DOCUMENT_TABLE and no --mock")
        api = client("dynamodb", cfg)
    print(
        asyncio.run(
            process_document(cfg, args.file, directory / "documents.db", dynamo=api, table=table)
        )
    )
    complete()


if __name__ == "__main__":
    run_cli(main)
