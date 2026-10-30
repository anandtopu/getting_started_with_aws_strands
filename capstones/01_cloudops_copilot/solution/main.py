"""CloudOps Copilot reference solution.

Run: uv run --all-groups python capstones/01_cloudops_copilot/solution/main.py --mock
Expected: checked evidence and Lesson complete. Mock cost $0; see README for opt-in AWS."""

import argparse

from common.capstone_ops import investigate
from common.config import ROOT
from common.lessons import complete, lesson_settings
from common.pretty import run_cli


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live-mcp", action="store_true")
    args, cfg = lesson_settings(parser)
    directory = ROOT / ".nimbus/capstones/01_cloudops_copilot"
    directory.mkdir(parents=True, exist_ok=True)
    # KEY IDEA: evidence and authorization are enforced by the host below the model.
    if args.mock and args.live_mcp:
        raise ValueError("Choose mock or live MCP, not both")
    print(investigate(cfg, directory, live_mcp=args.live_mcp))
    complete()


if __name__ == "__main__":
    run_cli(main)
