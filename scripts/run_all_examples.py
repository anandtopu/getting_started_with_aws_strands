"""Run every delivered example listed in the manifest; mocks are the default.

Run: uv run python scripts/run_all_examples.py
Cost: mock $0; --live --accept-cost calls the configured model. Resources: none.
Undelivered planned lessons are reported as such, never counted as passing examples.
"""

import argparse
import importlib.util
import json
import os
import subprocess
import sys

from common.config import ROOT, CourseError
from common.pretty import run_cli


def run_examples(*, live: bool = False, require_all: bool = False) -> int:
    # Captured child output is UTF-8; Windows terminals may use a narrower code page.
    # Preserve readable failure diagnostics rather than aborting the entire sweep.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    manifest = json.loads((ROOT / "scripts/examples_manifest.json").read_text(encoding="utf-8"))
    failed = 0
    checked = skipped = 0
    env = os.environ.copy()
    env.update(
        {"PYTHONUTF8": "1", "OTEL_SDK_DISABLED": "true", "LITELLM_LOCAL_MODEL_COST_MAP": "True"}
    )
    if not live:
        env["NIMBUS_OFFLINE"] = "1"
        env["AWS_EC2_METADATA_DISABLED"] = "true"
    env["MEM0_TELEMETRY"] = "false"
    for example in manifest["examples"]:
        missing = [
            name for name in example.get("requires", []) if importlib.util.find_spec(name) is None
        ]
        if missing:
            skipped += 1
            print(
                f"SKIP {example['path']}: install {example.get('install_hint', 'optional groups')}",
                flush=True,
            )
            continue
        checked += 1
        path = (ROOT / example["path"]).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise CourseError("Manifest example path is missing or outside this repository.")
        arguments = example["live_args"] if live else example["mock_args"]
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    *([] if live else [str(ROOT / "scripts/offline_run.py")]),
                    str(path),
                    *arguments,
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=example["timeout_seconds"],
                check=False,
            )
            passed = result.returncode == 0 and (
                live or example["expected_stdout"] in result.stdout
            )
            print(f"{'PASS' if passed else 'FAIL'} {example['path']}", flush=True)
            if not passed:
                # Errors from course CLIs are already sanitized; stderr may contain provider data.
                print(
                    f"Exit code: {result.returncode}; expected output matched: "
                    f"{example['expected_stdout'] in result.stdout}"
                )
                if not live:
                    print(result.stdout[-2000:])
                    print(result.stderr[-2000:])
                failed += 1
        except subprocess.TimeoutExpired:
            print(f"TIMEOUT {example['path']}")
            failed += 1
    print(
        f"Checked {checked} delivered entries; skipped {skipped} for missing dependencies. "
        "Skipped entries are not counted as passes."
    )
    return int(failed > 0 or (require_all and skipped > 0))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--accept-cost", action="store_true")
    parser.add_argument(
        "--require-all", action="store_true", help="Fail if optional dependencies are missing"
    )
    args = parser.parse_args()
    if args.live and not args.accept_cost:
        raise CourseError(
            "Live mode may be billable; add --accept-cost after reviewing configuration."
        )
    return run_examples(live=args.live, require_all=args.require_all)


if __name__ == "__main__":
    run_cli(main)
