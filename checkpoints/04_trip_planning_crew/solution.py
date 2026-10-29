"""Bounded specialist search with deterministic budget and approval routes.

Run: uv run python checkpoints/04_trip_planning_crew/solution.py --mock --decision approve
Expected: $528 draft; nothing booked or sent. Mock $0; live configured inference rates.
AWS resources created: none. Report: .nimbus/trip_crew_report.json.
"""

import argparse
import json

from common.config import ROOT
from common.coordination import report
from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.trip_graph import run_group_trip


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", choices=["approve", "reject", "ask"], default="reject")
    parser.add_argument("--budget-cents", type=int, default=100000)
    args, cfg = lesson_settings(parser)
    # KEY IDEA: model specialists suggest grounded quotes; host code owns the budget and approval.
    result, state = run_group_trip(
        cfg, decision=args.decision, budget_cents=args.budget_cents, specialist_search=True
    )
    record = report(result, cfg)
    review = state["review"]
    record.update(
        quote=review.quote.model_dump() if review else None,
        review_decision=review.decision if review else None,
        fingerprint=review.quote.fingerprint() if review else None,
        draft=state["draft"],
        booked=False,
        sent=False,
    )
    path = ROOT / ".nimbus/trip_crew_report.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("Draft:", record["draft"] or "None")
    print("Report:", path)
    complete()


if __name__ == "__main__":
    run_cli(main)
