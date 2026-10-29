"""Compare three providers using a small explicit rubric, costs and elapsed time.

Run: uv run python modules/02_model_providers/use_case/provider_comparison.py --mock
Expected: a Nimbus result followed by Lesson complete.
Cost: mock/local $0 hosted inference; hosted mode uses model tokens.
AWS resources created: none. Concepts: compose this module's taught APIs.
"""

import argparse
import csv
import time

from rich.table import Table
from strands import Agent

from common.config import ROOT, load_settings
from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, estimate_cost, run_cli


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--providers", nargs=3, default=["ollama", "bedrock", "openai"])
    args, cfg = lesson_settings(parser)
    questions = [
        ("Ask for my trip destination and budget.", ["destination", "budget"]),
        ("State that Nimbus prices are synthetic.", ["synthetic"]),
    ]
    table = Table("Provider", "Rubric hits", "Seconds", "Inference estimate")
    rows = []
    # KEY IDEA: identical prompts and a declared rubric make a comparison inspectable.
    for provider in args.providers:
        chosen = cfg if args.mock else load_settings(provider=provider)
        if not args.mock and provider != cfg.provider:
            chosen = chosen.model_copy(update={"input_price": None, "output_price": None})
        score, elapsed, cost = 0, 0.0, 0.0
        for prompt, required in questions:
            replies = ["What destination and budget? Prices are synthetic."]
            agent = Agent(
                model=get_model(chosen, responses=replies),
                callback_handler=None,
                retry_strategy=None,
            )
            start = time.perf_counter()
            result = agent(prompt, limits={"turns": 2})
            elapsed += time.perf_counter() - start
            score += int(all(word in str(result).lower() for word in required))
            estimate = estimate_cost(result.metrics.accumulated_usage, chosen)
            cost = None if cost is None or estimate is None else cost + estimate
        row = [
            provider,
            f"{score}/2",
            f"{elapsed:.3f}",
            "unknown" if cost is None else f"{cost:.6f}",
        ]
        rows.append(row)
        table.add_row(*row)
    console.print(table)
    console.print("Mode:", "script replay; not measured model quality" if args.mock else "live")
    output = ROOT / ".nimbus/provider_comparison.csv"
    output.parent.mkdir(exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["provider", "rubric_hits", "seconds", "usd"])
        writer.writerows(rows)
    complete()


if __name__ == "__main__":
    run_cli(main)
