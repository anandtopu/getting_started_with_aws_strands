"""Run the actual Strands Evals CLI with an offline guard and preserve its exit status."""

import argparse
import os
import subprocess
import sys

from common.config import ROOT


def gate(*, regression=False, live=False, fail_on="any"):
    from common.support_evaluation import experiment

    directory = ROOT / ".nimbus/evaluations"
    directory.mkdir(parents=True, exist_ok=True)
    source = directory / "support.json"
    experiment().to_file(str(source))
    result = subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8",
            "-m",
            "common.evaluation_cli",
            "--worker",
            "run",
            str(source),
            "--task",
            "common.support_evaluation:cli_task",
            "--custom-evaluator",
            "common.support_evaluation:PolicyEvidence",
            "--fail-on",
            fail_on,
            "--max-workers",
            "1",
            "--json",
            "-o",
            str(directory / ("regression.json" if regression else "baseline.json")),
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "NIMBUS_EVAL_REGRESSION": str(int(regression)),
            "NIMBUS_EVAL_LIVE": str(int(live)),
            "OTEL_SDK_DISABLED": "true",
        },
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=300,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError("Evaluation CLI failed: " + result.stderr[-1500:])
    return {
        "exit_code": result.returncode,
        "regression": regression,
        "report": str(directory / ("regression.json" if regression else "baseline.json")),
    }


def main():
    if "--worker" in sys.argv:
        from contextlib import nullcontext

        from strands_evals.cli.main import main as cli

        from common.network import offline_network

        sys.argv.remove("--worker")
        with nullcontext() if os.environ.get("NIMBUS_EVAL_LIVE") == "1" else offline_network():
            return cli()
    parser = argparse.ArgumentParser()
    parser.add_argument("--regression", action="store_true")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    result = gate(regression=args.regression, live=args.live)
    print(result)
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
