"""Approval web: Nimbus Tier 3 lesson.

Run: uv run --group apps python modules/12_interrupts/examples/04_approval_web.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from common.approvals import ApprovalLedger
from common.config import ROOT
from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.web_apps import demonstrate, serve


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true")
    args, cfg = lesson_settings(parser)
    if args.serve:
        serve(cfg, ledger=ApprovalLedger(ROOT / ".nimbus/approval_web.db"))
    else:
        with TemporaryDirectory() as directory:
            demonstrate(cfg, ledger=ApprovalLedger(Path(directory) / "approval.db"))
        complete()


if __name__ == "__main__":
    run_cli(main)
