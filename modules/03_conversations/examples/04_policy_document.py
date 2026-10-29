"""Document blocks on supported models; local PDF text extraction with page provenance.

Run: uv run python modules/03_conversations/examples/04_policy_document.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: Optional; local extraction. Resources created: none.
"""

import argparse

from pypdf import PdfReader
from strands import Agent

from common.data import data_path
from common.lessons import complete, lesson_settings, require_bedrock
from common.models import get_model
from common.pretty import run_cli


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", action="store_true", help="Use a Bedrock PDF content block")
    args, cfg = lesson_settings(parser)
    pdf = data_path("policies/nimbus_terms.pdf")
    if args.native:
        if not args.mock:
            require_bedrock(cfg)
        prompt = [
            {"text": "What is the refund threshold? Cite its PDF page."},
            {
                "document": {
                    "format": "pdf",
                    "name": "Nimbus policy",
                    "source": {"bytes": pdf.read_bytes()},
                }
            },
        ]
    else:
        # KEY IDEA: extracting text preserves page provenance even without native PDF support.
        text = "\n".join(
            f"[Page {i}] {p.extract_text()}" for i, p in enumerate(PdfReader(pdf).pages, 1)
        )
        prompt = "Use only this policy. Cite a page for supervisor approval.\n" + text
    result = Agent(
        model=get_model(cfg, responses=["Refunds over $500 need approval (page 3)."]),
        callback_handler=None,
        retry_strategy=None,
    )(prompt, limits={"turns": 2})
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
