"""Real Strands Evals cases and an offline quality gate for the deployed support core."""

import os

from strands_evals import Case, Experiment
from strands_evals.evaluators import Evaluator, OutputEvaluator, TrajectoryEvaluator
from strands_evals.evaluators.deterministic import ToolCalled
from strands_evals.types.evaluation import EvaluationData, EvaluationOutput

from common.config import load_settings
from common.data import load_jsonl
from common.models import get_model
from common.production_support import answer_support
from common.testing import tool_message


class PolicyEvidence(Evaluator):
    """Require expected phrases and citation; these are checks, not semantic factuality proof."""

    def evaluate(self, evaluation_case):
        expected = evaluation_case.expected_output
        answer = str(evaluation_case.actual_output).lower()
        if expected.get("abstain"):
            passed = "cannot" in answer and "visa" in answer
        else:
            passed = all(term.lower() in answer for term in expected["terms"])
            passed = passed and expected["source"].lower() in answer
        return [
            EvaluationOutput(
                score=float(passed),
                test_pass=passed,
                reason="Required policy evidence/citation or abstention",
            )
        ]

    async def evaluate_async(self, evaluation_case):
        return self.evaluate(evaluation_case)


def experiment():
    rows = load_jsonl("eval/policy_qa.jsonl")
    cases = [
        Case(
            name=row["id"],
            input=row["input"],
            expected_output={
                "terms": row.get("expected_terms", []),
                "source": row.get("source", ""),
                "abstain": row.get("expected_behavior") == "abstain",
            },
            expected_trajectory=["search_policies"],
        )
        for row in rows
    ]
    return Experiment(cases=cases, evaluators=[PolicyEvidence(), ToolCalled("search_policies")])


async def evaluate_support(settings, *, regression=False):
    async def task(case):
        result = await answer_support({"prompt": case.input}, settings, regression=regression)
        return {"output": result["answer"], "trajectory": result["tools"]}

    return await experiment().run_evaluations_async(task, max_workers=1)


async def cli_task(case):
    """CLI factory: offline by default; explicit course environment enables a live model."""
    cfg = load_settings(provider=None if os.environ.get("NIMBUS_EVAL_LIVE") == "1" else "mock")
    result = await answer_support(
        {"prompt": case.input}, cfg, regression=os.environ.get("NIMBUS_EVAL_REGRESSION") == "1"
    )
    return {"output": result["answer"], "trajectory": result["tools"]}


async def judge_demo(settings):
    """Exercise both judge classes; scripted ratings verify plumbing, not answer quality."""
    data = EvaluationData(
        input="How long does an approved refund take?",
        actual_output="5 to 10 business days [policies/refund.md]",
        expected_output="5 to 10 business days",
        actual_trajectory=["search_policies"],
        expected_trajectory=["search_policies"],
    )
    result = []
    for cls in (OutputEvaluator, TrajectoryEvaluator):
        judge = cls(
            rubric="Score supported policy facts and correct tool use; reject invention.",
            model=get_model(
                settings,
                responses=[
                    tool_message(
                        "EvaluationOutput",
                        {"score": 1.0, "test_pass": True, "reason": "Scripted judge rating"},
                    )
                ],
            ),
        )
        result.extend(output.model_dump() for output in await judge.evaluate_async(data))
    return result
