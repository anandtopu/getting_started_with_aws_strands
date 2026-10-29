"""Persist explicit Ollama vectors in Chroma; reopen without re-embedding the corpus.

Run: uv run --group rag python modules/07_rag/examples/03_local_index.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

from common.config import ROOT
from common.lessons import complete, lesson_settings
from common.models import get_embeddings
from common.pretty import console, run_cli
from common.retrieval import LocalIndex, load_chunks


def main() -> None:
    args, cfg = lesson_settings()
    embed = get_embeddings(mock=args.mock)
    directory = ROOT / ".nimbus" / ("chroma_mock" if args.mock else "chroma_ollama")
    index = LocalIndex(directory, embed)
    index.replace(load_chunks())
    # KEY IDEA: the same embedding identity must serve indexing and querying.
    reopened = LocalIndex(directory, embed)
    console.print(reopened.search("approved refund timing", topic="refund"))
    complete()


if __name__ == "__main__":
    run_cli(main)
