"""Classify the held-out ticket subset, export CSV, and score after prediction.

Run: uv run python modules/04_structured_output/use_case/ticket_triage.py --mock
Expected: a Nimbus result followed by Lesson complete.
Cost: mock/local $0 hosted inference; hosted mode uses model tokens.
AWS resources created: none. Concepts: compose this module's taught APIs.
"""

import csv

from strands import Agent

from common.config import ROOT
from common.data import load_jsonl
from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, estimate_cost, run_cli
from common.schemas import TicketTriage
from common.testing import tool_message
from common.triage import fixture_triage


def main() -> None:
    _, cfg = lesson_settings()
    cases = load_jsonl("eval/ticket_triage.jsonl")
    rows, correct = [], 0
    usage = {"inputTokens": 0, "outputTokens": 0}
    # KEY IDEA: labels are read by the scorer, never put in the agent's prompt.
    for item in cases:
        scripted = fixture_triage(item["input"])
        agent = Agent(
            model=get_model(cfg, responses=[tool_message("TicketTriage", scripted)]),
            structured_output_model=TicketTriage,
            callback_handler=None,
            retry_strategy=None,
        )
        result = agent(
            "Classify this Nimbus ticket. High urgency means departure within 24 hours. "
            + item["input"],
            limits={"turns": 3},
        )
        prediction = result.structured_output
        for key in usage:
            usage[key] += result.metrics.accumulated_usage.get(key, 0)
        if prediction is None:
            raise RuntimeError("No valid classification within the turn budget")
        match = all(getattr(prediction, key) == value for key, value in item["expected"].items())
        correct += int(match)
        rows.append({"id": item["id"], **prediction.model_dump(mode="json"), "correct": match})
    output = ROOT / ".nimbus/ticket_triage.csv"
    output.parent.mkdir(exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    console.print(f"Exact category+urgency accuracy: {correct}/{len(cases)}")
    console.print("Replay validates scoring/CSV only; run live to measure the selected model.")
    console.print("CSV:", str(output))
    console.print("Total token usage:", usage, "Inference estimate USD:", estimate_cost(usage, cfg))
    complete()


if __name__ == "__main__":
    run_cli(main)
