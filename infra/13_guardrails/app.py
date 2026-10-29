"""Synthesize only; CDK deploy is an explicit optional learner action."""

import os

import aws_cdk as cdk

from common.config import course_value
from common.guardrail_stack import GuardrailStack

app = cdk.App()
GuardrailStack(
    app,
    "NimbusGuardrailLab",
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT", "111122223333"),
        region=os.environ.get("CDK_DEFAULT_REGION") or course_value("AWS_REGION"),
    ),
)
app.synth()
