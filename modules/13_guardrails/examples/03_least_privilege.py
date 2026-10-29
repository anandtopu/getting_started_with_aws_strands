"""Least privilege: Nimbus Tier 3 lesson.

Run: uv run python modules/13_guardrails/examples/03_least_privilege.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

import sqlite3
from importlib import import_module

from common.data import bookings_connection
from common.lessons import complete, lesson_settings
from common.pretty import run_cli


def main():
    lesson_settings()
    with bookings_connection() as db:
        try:
            db.execute("CREATE TABLE forbidden (id INTEGER)")
        except sqlite3.OperationalError:
            print("Read-only database rejected a write")
    import json

    from common.config import ROOT

    policy = json.loads((ROOT / "modules/13_guardrails/read_only_aws_policy.json").read_text())
    print("Scoped use_aws discovery policy:", policy)
    # Reuse the same reviewed read-only wrapper and Stubber/live path taught in Module 06.
    # Its application check rejects terminate_instances before any request can be sent.
    demo = import_module("modules.06_community_tools.examples.05_read_only_aws")
    demo.main()
    complete()


if __name__ == "__main__":
    run_cli(main)
