"""Ask Nimbus: persistent vector retrieval and evidence-checked policy answers.

Run: uv run --group rag python modules/07_rag/use_case/ask_nimbus.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

from common.config import ROOT
from common.lessons import complete, lesson_settings
from common.models import get_embeddings
from common.pretty import console, run_cli
from common.rag_agent import answer_policy
from common.retrieval import LocalIndex, load_chunks


def main() -> None:
    args, cfg = lesson_settings()
    chunks = load_chunks(pdf=True)
    by_id = {c.id: c for c in chunks}
    index = LocalIndex(
        ROOT / ".nimbus" / ("ask_nimbus_mock" if args.mock else "ask_nimbus_live"),
        get_embeddings(mock=args.mock),
    )
    index.replace(chunks)
    # KEY IDEA: retrieve IDs map to authoritative stored chunks, never model-invented filenames.
    result, _ = answer_policy(
        cfg,
        "How long does an approved refund take?",
        chunks,
        retrieve=lambda query: [by_id[row["id"]] for row in index.search(query)],
    )
    console.print(result.structured_output.model_dump())
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
