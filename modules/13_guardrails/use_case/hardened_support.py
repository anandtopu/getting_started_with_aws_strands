"""Dened support: Nimbus Tier 3 lesson.

Run: uv run python modules/13_guardrails/use_case/hardened_support.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from common.approvals import ApprovalLedger, approval_agent, request_prompt, responses_for
from common.audit import AuditPolicy
from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.safety import injection_trial


def main():
    _, cfg = lesson_settings()
    print("Injected document:", injection_trial(cfg, hardened=True))
    with TemporaryDirectory() as directory:
        ledger = ApprovalLedger(Path(directory) / "support.db")
        key = ledger.propose("CUS-001", "DEMO-001", "refund", 60000)
        audit = AuditPolicy(allowed=("apply_action",), max_tools=2)
        agent = approval_agent(cfg, ledger, key, hooks=[audit])
        result = agent(request_prompt(ledger, key), limits={"turns": 3})
        if result.stop_reason == "interrupt":
            ledger.decide(key, "CUS-001", "reject", supervisor="SUPERVISOR-DEMO")
            result = agent(responses_for(result), limits={"turns": 3})
        print("Final status:", ledger.get(key, "CUS-001")["status"], "audit:", audit.rows)
        complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
