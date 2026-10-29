"""Export measured before/after retrieval results without claiming invented improvements.

Run: uv run --group rag python modules/08_advanced_rag/use_case/retrieval_comparison.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

import argparse
import json

from common.config import ROOT
from common.data import load_jsonl
from common.lessons import complete, lesson_settings
from common.models import get_embeddings
from common.pretty import console, run_cli
from common.retrieval_evaluation import evaluate_answers, retrieval_report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--judge-answers", action="store_true", help="Generate and judge all 12 answers"
    )
    args, cfg = lesson_settings(parser)
    # KEY IDEA: report the observed difference, including a tie or regression.
    report = retrieval_report(load_jsonl("eval/policy_qa.jsonl"), get_embeddings(mock=args.mock))
    if args.judge_answers:
        report["answer_evaluation"] = evaluate_answers(cfg, load_jsonl("eval/policy_qa.jsonl"))
    path = ROOT / ".nimbus/retrieval_report.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    console.print("Method | source hit rate @3")
    console.print("Lexical |", report["baseline_hit_rate"])
    console.print("Hybrid  |", report["hybrid_hit_rate"])
    console.print("Report:", str(path), "Mode:", report["mode"])
    complete()


if __name__ == "__main__":
    run_cli(main)
