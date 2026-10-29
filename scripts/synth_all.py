"""Synthesize delivered CDK apps; never bootstrap or deploy.

Run: uv run python scripts/synth_all.py
Expected until Tier 5: no CDK applications delivered. AWS cost/resources: none.
"""

import shutil
import subprocess

from common.config import ROOT


def main() -> int:
    apps = sorted((ROOT / "infra").glob("*/cdk.json"))
    if not apps:
        print("No CDK apps delivered yet. No synthesis or deployment claimed.")
        return 0
    executable = shutil.which("cdk")
    if not executable:
        print("Install the documented Node.js CDK CLI before synthesizing infrastructure.")
        return 1
    failed = False
    for app in apps:
        result = subprocess.run(
            [executable, "synth", "--no-lookups"], cwd=app.parent, check=False, timeout=180
        )
        failed |= result.returncode != 0
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
