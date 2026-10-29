"""Python, uv, pip/venv fallback, Ollama tool-capable model and configuration checks.

Run: uv run python modules/00_setup/examples/02_local_readiness.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

import argparse
import sys

from common.config import load_settings
from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli
from scripts.check_env import check_ollama


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-service", action="store_true")
    args, cfg = lesson_settings(parser)
    console.print("Python", sys.version.split()[0], "provider", cfg.provider)
    console.print("Free path: set MODEL_PROVIDER=ollama; leave MODEL_ID blank.")
    if args.check_service and not args.mock:
        check_ollama(load_settings(provider="ollama"))
    else:
        console.print("Offline configuration check; Ollama service not contacted.")
    # KEY IDEA: configuration readiness and service reachability are separate checks.
    assert get_model(provider="mock", responses=["ready"]).get_config()["model_id"] == "scripted"
    complete()


if __name__ == "__main__":
    run_cli(main)
