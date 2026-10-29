"""Console and real local OTLP spans: Nimbus production lesson.

Run: uv run --all-groups python modules/19_observability/examples/02_local_tracing.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

import argparse
import os
import subprocess
import sys

from common.lessons import complete, lesson_settings
from common.pretty import run_cli


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--otlp", help="Local Jaeger endpoint, http://127.0.0.1:4318/v1/traces")
    args, cfg = lesson_settings(parser)
    # KEY IDEA: process globals require a fresh tracer process, including in notebooks.
    command = [sys.executable, "-X", "utf8", "-m", "common.telemetry_lab"]
    if args.mock:
        command.append("--mock")
    if args.otlp:
        command.extend(["--otlp", args.otlp])
    subprocess.run(command, env={**os.environ, "PYTHONUTF8": "1"}, check=True, timeout=60)
    complete()


if __name__ == "__main__":
    run_cli(main)
