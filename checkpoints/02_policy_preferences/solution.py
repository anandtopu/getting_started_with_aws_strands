"""Combine cited policy answers, scoped preferences, sessions and an evaluation report.

Run: uv run --group rag python checkpoints/02_policy_preferences/solution.py --mock
Expected: cited answer, retrieval report and verified user deletion.
Cost: offline $0; live inference/embeddings use tokens. AWS resources: none.
"""

import json
import tempfile
from pathlib import Path

from common.config import ROOT
from common.data import load_jsonl
from common.lessons import complete, lesson_settings
from common.models import get_embeddings
from common.preferences import Preferences
from common.pretty import console, run_cli
from common.rag_agent import answer_policy
from common.retrieval import load_chunks
from common.retrieval_evaluation import retrieval_report


def main() -> None:
    args, cfg = lesson_settings()
    with tempfile.TemporaryDirectory(prefix="nimbus-checkpoint-") as directory:
        store = Preferences(Path(directory))
        store.save("CUS-001", "seat", "aisle", consent=True)
        store.save("CUS-002", "meal", "vegetarian", consent=True)
        # KEY IDEA: derive identity in application code, then attach only that user's data.
        result, evidence = answer_policy(
            cfg,
            "approved refund timing",
            load_chunks(pdf=True),
            session_manager=store.session("CUS-001", "support"),
            preferences=store.read("CUS-001"),
        )
        console.print(result.structured_output.model_dump())
        console.print("Evidence chunks:", len(evidence))
        report = retrieval_report(
            load_jsonl("eval/policy_qa.jsonl"), get_embeddings(mock=args.mock)
        )
        output = ROOT / ".nimbus/policy_preferences_report.json"
        output.parent.mkdir(exist_ok=True)
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        store.delete_user("CUS-001")
        assert store.read("CUS-001") == {}
        assert store.read("CUS-002") == {"meal": "vegetarian"}
        console.print("User deletion verified; report:", str(output))
        complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
