"""Measure held-out source hits and demonstrate a separate answer judge.

Run: uv run --group rag python modules/08_advanced_rag/examples/05_evaluate_retrieval.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

from common.data import load_jsonl
from common.lessons import complete, lesson_settings
from common.models import get_embeddings
from common.pretty import console, run_cli
from common.retrieval_evaluation import judge_answer, retrieval_report


def main() -> None:
    args, cfg = lesson_settings()
    # KEY IDEA: a correct retrieved source does not establish a correct final answer.
    report = retrieval_report(load_jsonl("eval/policy_qa.jsonl"), get_embeddings(mock=args.mock))
    console.print({key: value for key, value in report.items() if key != "rows"})
    result = judge_answer(
        cfg,
        "When does approval expire?",
        "After 30 days.",
        "Approval expires after 30 minutes.",
        "30 minutes",
    )
    console.print("Separate judge:", result.structured_output)
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
