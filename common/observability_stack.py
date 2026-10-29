"""A bounded log/metric destination; no account-wide Transaction Search changes."""

from aws_cdk import CfnOutput, Duration, Stack, Tags
from aws_cdk import aws_cloudwatch as cw
from aws_cdk import aws_iam as iam

from common.hosting_stacks import log_group
from common.infra_stacks import PROJECT


class ObservabilityStack(Stack):
    def __init__(self, scope, name, **kwargs):
        super().__init__(scope, name, **kwargs)
        Tags.of(self).add("project", PROJECT)
        group = log_group(self, "PublicMetrics")
        policy = iam.ManagedPolicy(
            self,
            "TelemetryWriter",
            statements=[
                # X-Ray OTLP ingestion uses this action and has no resource-level ARN support.
                iam.PolicyStatement(actions=["xray:PutTraceSegments"], resources=["*"]),
                # PutMetricData has no resource ARN; its namespace condition narrows writes.
                iam.PolicyStatement(
                    actions=["cloudwatch:PutMetricData"],
                    resources=["*"],
                    conditions={"StringEquals": {"cloudwatch:namespace": "Nimbus/Course"}},
                ),
                # Write content-free diagnostics only into this seven-day group.
                iam.PolicyStatement(
                    actions=["logs:CreateLogStream", "logs:PutLogEvents"],
                    resources=[group.log_group_arn],
                ),
            ],
        )
        cw.Alarm(
            self,
            "SlowResponses",
            metric=cw.Metric(
                namespace="Nimbus/Course",
                metric_name="Latency",
                period=Duration.minutes(5),
                statistic="p95",
            ),
            threshold=20,
            evaluation_periods=1,
            treat_missing_data=cw.TreatMissingData.NOT_BREACHING,
        )
        CfnOutput(self, "LogGroup", value=group.log_group_name)
        CfnOutput(self, "TelemetryPolicyArn", value=policy.managed_policy_arn)
