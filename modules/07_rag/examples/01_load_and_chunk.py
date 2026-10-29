"""Load approved Markdown and PDF policies with stable source/page citations.

Run: uv run python modules/07_rag/examples/01_load_and_chunk.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

from common.lessons import complete, lesson_settings
from common.pretty import console, run_cli
from common.retrieval import load_chunks, split_text


def main() -> None:
    args, cfg = lesson_settings()
    try:
        split_text("A chunk must advance", size=3, overlap=3)
    except ValueError as exc:
        console.print("Failure before fix:", str(exc))
    # KEY IDEA: never concatenate PDF pages before assigning provenance.
    for chunk in load_chunks(pdf=True)[:3]:
        console.print(chunk.record())
    console.print("Markdown chunks:", len(load_chunks()))
    complete()


if __name__ == "__main__":
    run_cli(main)
