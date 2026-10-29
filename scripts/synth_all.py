"""Synthesize delivered CDK apps; never bootstrap or deploy.

Run: uv run python scripts/synth_all.py
Expected: all delivered apps synthesize locally. AWS cost/resources: none.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from common.config import ROOT


def main() -> int:
    apps = sorted((ROOT / "infra").glob("*/cdk.json"))
    if not apps:
        print("No CDK apps delivered yet. No synthesis or deployment claimed.")
        return 0
    local_cli = ROOT / "infra/node_modules/aws-cdk/bin/cdk"
    command = (
        [shutil.which("node"), str(local_cli)]
        if local_cli.exists() and shutil.which("node")
        else [shutil.which("cdk")]
    )
    if not command[0]:
        print("Install Node.js 22+ and run npm ci --prefix infra before synthesis.")
        return 1
    failed = False
    for app in apps:
        result = subprocess.run(
            [*command, "synth", "--no-lookups", "--quiet", "--no-notices", "--no-telemetry"],
            cwd=app.parent,
            env={
                **os.environ,
                "PATH": str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"],
                "CDK_DEFAULT_ACCOUNT": "111122223333",
                "AWS_EC2_METADATA_DISABLED": "true",
                "CDK_DISABLE_VERSION_CHECK": "1",
            },
            check=False,
            timeout=180,
        )
        failed |= result.returncode != 0
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
