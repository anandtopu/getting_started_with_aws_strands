"""Synthesize a tagged, pay-per-request document table; never deploy implicitly."""

import os

import aws_cdk as cdk
from aws_cdk import aws_dynamodb as dynamo
from aws_cdk import aws_iam as iam

from common.config import course_value
from common.infra_stacks import PROJECT

app = cdk.App(outdir=os.environ.get("CDK_OUTDIR"))
stack = cdk.Stack(
    app,
    "NimbusDocuments",
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT", "111122223333"),
        region=course_value("AWS_REGION"),
    ),
)
cdk.Tags.of(stack).add("project", PROJECT)
table = dynamo.Table(
    stack,
    "Documents",
    partition_key=dynamo.Attribute(name="sha", type=dynamo.AttributeType.STRING),
    billing_mode=dynamo.BillingMode.PAY_PER_REQUEST,
    removal_policy=cdk.RemovalPolicy.DESTROY,
)
# Read and conditionally write this table; no scans or administration for the pipeline.
policy = iam.ManagedPolicy(
    stack,
    "DocumentAccess",
    statements=[
        iam.PolicyStatement(
            actions=["dynamodb:PutItem", "dynamodb:GetItem"], resources=[table.table_arn]
        )
    ],
)
cdk.CfnOutput(stack, "TableName", value=table.table_name)
cdk.CfnOutput(stack, "AccessPolicyArn", value=policy.managed_policy_arn)
app.synth()
