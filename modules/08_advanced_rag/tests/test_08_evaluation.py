"""Test budgets, rank fusion, label separation and citation failure cases."""

import pytest

from common.config import load_settings
from common.models import get_embeddings
from common.retrieval import Chunk, hybrid_search
from common.retrieval_evaluation import judge_answer, retrieval_report


def test_hybrid_results_are_unique_and_bounded():
    pytest.importorskip("rank_bm25")
    chunks = [
        Chunk(str(i), text, f"{i}.md", 0, "demo")
        for i, text in enumerate(
            ["refund refund timing", "seat preference", "refund approval", "meal vegetarian"]
        )
    ]
    hits = hybrid_search(chunks, "refund timing", get_embeddings(mock=True), k=2)
    assert len(hits) == len({c.id for c in hits}) == 2
    assert hits[0].id == "0"


def test_labels_do_not_change_retrieval():
    pytest.importorskip("rank_bm25")
    original = [{"id": "x", "input": "refund timing", "source": "policies/refund.md"}]
    changed = [{**original[0], "source": "invented.md"}]
    one = retrieval_report(original, get_embeddings(mock=True))["rows"][0]
    two = retrieval_report(changed, get_embeddings(mock=True))["rows"][0]
    assert one["hybrid_ids"] == two["hybrid_ids"]
    assert not two["hybrid_hit"]


def test_mock_judge_reports_scripted_failure_without_claiming_quality():
    result = judge_answer(
        load_settings(provider="mock"), "When?", "30 days", "30 minutes", "30 minutes"
    )
    assert result.structured_output.correct is False
    assert "Scripted" in result.structured_output.explanation


def test_answer_report_separates_judge_scores():
    from common.retrieval_evaluation import evaluate_answers

    report = evaluate_answers(
        load_settings(provider="mock"),
        [{"id": "demo", "input": "refund timing", "expected_terms": ["5 to 10 business days"]}],
    )
    assert report["faithfulness"] == 0
    assert report["correctness"] == 0
    assert "not model-quality evidence" in report["mode"]
