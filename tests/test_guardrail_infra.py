"""Optional resource synthesis and model attachment without paid calls."""

import pytest


def test_guardrail_template(tmp_path):
    cdk = pytest.importorskip("aws_cdk")
    from aws_cdk.assertions import Template

    from common.guardrail_stack import GuardrailStack

    app = cdk.App(outdir=str(tmp_path))
    stack = GuardrailStack(
        app, "Guardrail", env=cdk.Environment(account="111122223333", region="us-east-1")
    )
    template = Template.from_stack(stack).to_json()
    guard = next(
        r["Properties"]
        for r in template["Resources"].values()
        if r["Type"] == "AWS::Bedrock::Guardrail"
    )
    assert len(guard["ContentPolicyConfig"]["FiltersConfig"]) == 5
    assert (
        guard["SensitiveInformationPolicyConfig"]["PiiEntitiesConfig"][0]["Action"] == "ANONYMIZE"
    )
    assert len(guard["ContextualGroundingPolicyConfig"]["FiltersConfig"]) == 2
    policy = next(
        r["Properties"]
        for r in template["Resources"].values()
        if r["Type"] == "AWS::IAM::ManagedPolicy"
    )
    assert policy["PolicyDocument"]["Statement"][0]["Action"] == "bedrock:ApplyGuardrail"
    app.synth()


def test_model_attaches_guardrail(monkeypatch):
    from common.config import load_settings
    from common.models import get_guarded_model

    monkeypatch.setenv("BEDROCK_GUARDRAIL_ID", "demo123456")
    monkeypatch.setenv("BEDROCK_GUARDRAIL_VERSION", "1")
    cfg = load_settings(provider="bedrock").model_copy(update={"aws_profile": ""})
    model = get_guarded_model(cfg)
    request = model.format_request([{"role": "user", "content": [{"text": "Travel question"}]}])
    assert request["guardrailConfig"]["guardrailIdentifier"] == "demo123456"
    assert request["guardrailConfig"]["streamProcessingMode"] == "sync"
