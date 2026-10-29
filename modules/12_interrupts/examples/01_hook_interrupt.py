"""Hook interrupt: Nimbus Tier 3 lesson.

Run: uv run python modules/12_interrupts/examples/01_hook_interrupt.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from common.approvals import ApprovalLedger, approval_agent, request_prompt, responses_for
from common.lessons import complete, lesson_settings
from common.pretty import run_cli


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--decision", choices=["approve", "reject", "expire", "ask"], default="reject"
    )
    parser.add_argument("--action", choices=["refund", "change"], default="refund")
    args, cfg = lesson_settings(parser)
    with TemporaryDirectory() as directory:
        ledger = ApprovalLedger(Path(directory) / "approval.db")
        key = ledger.propose(
            "CUS-001", "DEMO-001", args.action, 60000 if args.action == "refund" else 0
        )
        agent = approval_agent(cfg, ledger, key)
        result = agent(request_prompt(ledger, key), limits={"turns": 3})
        if result.stop_reason == "interrupt":
            print("Review exact terms:", result.interrupts[0].reason)
            decision = (
                input("approve/reject: ").strip() if args.decision == "ask" else args.decision
            )
            expired = ledger.get(key, "CUS-001")["expires"] if decision == "expire" else None
            ledger.decide(
                key,
                "CUS-001",
                "approve" if decision in {"approve", "expire"} else "reject",
                supervisor="SUPERVISOR-DEMO",
                now=expired,
            )
            result = agent(responses_for(result), limits={"turns": 3})
        print("Authoritative status:", ledger.get(key, "CUS-001")["status"])
        complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
