"""Independent ground truth and report artifacts, with no AWS calls."""

import json
from pathlib import Path

import pytest

from common.capstone_ops import analyze_costs, analyze_logs, investigate
from common.config import load_settings
from common.data import load_csv, load_jsonl


def test_heldout_incidents_and_cost_candidates():
    expected = json.loads((Path(__file__).parents[1] / "evaluation.json").read_text())
    incidents = analyze_logs(load_jsonl("ops/app_logs.jsonl"))
    assert [x["date"] for x in incidents] == expected["incident_days"]
    assert [x["kind"] for x in incidents] == expected["kinds"]
    assert set(analyze_costs(load_csv("ops/cost_report.csv"))["review_candidates"]) == set(
        expected["cost_candidates"]
    )
    assert analyze_logs([]) == []


def test_reports_and_chart(tmp_path):
    pytest.importorskip("matplotlib")
    report = investigate(load_settings(provider="mock"), tmp_path)
    assert len(report["incidents"]) == 3
    assert report["runbook_sources"]
    assert (tmp_path / "costs.png").read_bytes().startswith(b"\x89PNG")
    assert all(
        (tmp_path / name).is_file()
        for name in ("incident-summary.md", "cost-savings.md", "evidence.json")
    )
