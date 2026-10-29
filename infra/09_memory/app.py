"""Synthesize the optional NimbusMemoryLab; deployment is a separate explicit command."""

import os

from aws_cdk import App, Environment

from common.config import course_value
from common.infra_stacks import MemoryStack

app = App()
MemoryStack(
    app,
    "NimbusMemoryLab",
    env=Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT", "111122223333"),
        region=os.environ.get("CDK_DEFAULT_REGION") or course_value("AWS_REGION"),
    ),
)
app.synth()
