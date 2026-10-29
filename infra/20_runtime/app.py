"""Synthesis only; deployment is an explicit learner action."""

import os

import aws_cdk as cdk

from common.config import course_value
from common.hosting_stacks import RuntimeStack

app = cdk.App(context={"@aws-cdk/core:validateAgainstDefaultRules": True})
RuntimeStack(
    app,
    "NimbusRuntime",
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT", "111122223333"),
        region=os.environ.get("CDK_DEFAULT_REGION") or course_value("AWS_REGION"),
    ),
)
app.synth()
