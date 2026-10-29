"""Image content blocks and vision capability checks on a synthetic receipt.

Run: uv run python modules/03_conversations/examples/03_receipt_image.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No; vision model needed. Resources created: none.
"""

import os

from strands import Agent

from common.config import ROOT, load_settings
from common.data import data_path
from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli


def main() -> None:
    args, cfg = lesson_settings()
    if cfg.provider == "ollama":
        env = {**os.environ, "MODEL_ID": os.environ.get("OLLAMA_VISION_MODEL_ID", "")}
        if not env["MODEL_ID"]:
            from dotenv import dotenv_values

            env["MODEL_ID"] = dotenv_values(ROOT / ".env.example")["OLLAMA_VISION_MODEL_ID"]
        cfg = load_settings(environ=env)
    # KEY IDEA: image bytes are an image block, not text describing a file path.
    prompt = [
        {"text": "Read this synthetic receipt. Report the displayed total; do not guess."},
        {
            "image": {
                "format": "png",
                "source": {"bytes": data_path("receipts/receipt_01.png").read_bytes()},
            }
        },
    ]
    agent = Agent(
        model=get_model(cfg, responses=["Receipt RCP-001 displays USD 160.60."]),
        callback_handler=None,
        retry_strategy=None,
    )
    console.print("Live mode requires vision support; mock does not evaluate image recognition.")
    complete(agent(prompt, limits={"turns": 2}), cfg)


if __name__ == "__main__":
    run_cli(main)
