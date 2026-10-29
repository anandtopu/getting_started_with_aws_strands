"""Human review before confirmation draft: Nimbus Tier 4 lesson.

Run: uv run python modules/17_graphs/examples/06_approval_pipeline.py --mock
Expected: Lesson complete. Mock fixtures cost $0; Ollama has no API fee.
Live inference uses configured rates and bounded calls. AWS resources created: none.
"""

import argparse

from common.coordination import report
from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.trip_graph import run_group_trip


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", choices=["approve", "reject", "ask"], default="reject")
    parser.add_argument("--budget-cents", type=int, default=100000)
    args, cfg = lesson_settings(parser)
    # KEY IDEA: the host records approval of the exact quote; model text grants no authority.
    result, state = run_group_trip(cfg, decision=args.decision, budget_cents=args.budget_cents)
    report(result, cfg)
    print("Draft:", state["draft"] or "None: review not approved or over budget")
    complete()


if __name__ == "__main__":
    run_cli(main)
