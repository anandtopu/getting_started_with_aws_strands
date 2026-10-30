"""Partner Network reference solution.

Run: uv run --all-groups python capstones/05_partner_network/solution/main.py --mock
Expected: checked evidence and Lesson complete. Mock cost $0; see README for opt-in AWS."""

import argparse
import asyncio

from common.config import ROOT
from common.lessons import complete, lesson_settings
from common.partner_client import ask_partner, partner_process
from common.pretty import run_cli


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["strands", "langgraph"], default="langgraph")
    args, cfg = lesson_settings(parser)
    directory = ROOT / ".nimbus/capstones/05_partner_network"
    directory.mkdir(parents=True, exist_ok=True)
    # KEY IDEA: evidence and authorization are enforced by the host below the model.
    with partner_process(cfg, backend=args.backend) as (url, token):
        print(asyncio.run(ask_partner(url, token, streaming=True)))
    complete()


if __name__ == "__main__":
    run_cli(main)
