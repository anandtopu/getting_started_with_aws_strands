"""AWS optional: supported memory-store retrieval with an exact metadata filter.

Run: uv run python modules/07_rag/examples/05_knowledge_base.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

import asyncio

from common.aws_retrieval import knowledge_store
from common.lessons import complete, lesson_settings
from common.pretty import console, run_cli


def main() -> None:
    args, cfg = lesson_settings()
    with knowledge_store(args.mock) as store:
        # KEY IDEA: a read-only store replaces the deprecated retrieve community tool.
        entries = asyncio.run(store.search("refund timing"))
        console.print(entries)
    complete()


if __name__ == "__main__":
    run_cli(main)
