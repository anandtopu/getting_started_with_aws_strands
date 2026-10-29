"""Tagged AgentCore services and disabled-by-default managed evaluation schedules."""

import shutil

from aws_cdk import CfnOutput, CfnParameter, Duration, RemovalPolicy, Stack, Tags
from aws_cdk import aws_bedrockagentcore as ac
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_ecr_assets as assets
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lam
from aws_cdk import aws_scheduler as scheduler

from common.config import ROOT
from common.hosting_stacks import log_group, write_logs
from common.infra_stacks import PROJECT, bucket
from scripts.prepare_deployment import clean_generated_context, prepare


def gateway_package():
    path = ROOT / ".nimbus/gateway-package"
    clean_generated_context(path)
    (path / "common").mkdir(parents=True, exist_ok=True)
    (path / "data").mkdir(exist_ok=True)
    for file in ("__init__.py", "public_booking.py"):
        shutil.copyfile(ROOT / "common" / file, path / "common" / file)
    shutil.copyfile(ROOT / "data/flights.csv", path / "data/flights.csv")
    return str(path)


class AgentCoreStack(Stack):
    def __init__(self, scope, name, **kwargs):
        super().__init__(scope, name, **kwargs)
        Tags.of(self).add("project", PROJECT)
        enabled = CfnParameter(
            self,
            "EvaluationScheduleState",
            default="DISABLED",
            allowed_values=["DISABLED", "ENABLED"],
        )
        pool = cognito.UserPool(
            self,
            "Travelers",
            self_sign_up_enabled=False,
            sign_in_aliases=cognito.SignInAliases(email=True),
            removal_policy=RemovalPolicy.DESTROY,
        )
        resource = pool.add_resource_server(
            "Scopes",
            identifier="nimbus",
            scopes=[
                cognito.ResourceServerScope(
                    scope_name="read", scope_description="Read public booking quotes"
                )
            ],
        )
        app_client = pool.add_client(
            "WebClient",
            generate_secret=False,
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True),
                scopes=[
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.resource_server(
                        resource,
                        cognito.ResourceServerScope(
                            scope_name="read", scope_description="Read public booking quotes"
                        ),
                    ),
                ],
                callback_urls=["http://localhost:8765/callback"],
            ),
        )
        domain = pool.add_domain(
            "Login",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=f"nimbus-{self.account}-{self.region}"
            ),
        )
        memory = ac.CfnMemory(
            self,
            "Memory",
            name="NimbusProductionPreferences",
            event_expiry_duration=7,
            memory_strategies=[
                {
                    "userPreferenceMemoryStrategy": {
                        "name": "Preferences",
                        "namespaces": ["/preferences/{actorId}/"],
                    }
                },
                {"semanticMemoryStrategy": {"name": "Facts", "namespaces": ["/facts/{actorId}/"]}},
                {
                    "summaryMemoryStrategy": {
                        "name": "Summary",
                        "namespaces": ["/summaries/{actorId}/{sessionId}/"],
                    }
                },
                {
                    "episodicMemoryStrategy": {
                        "name": "Episodes",
                        "namespaces": ["/episodes/{actorId}/"],
                    }
                },
            ],
        )
        engine = ac.CfnPolicyEngine(self, "PolicyEngine", name="NimbusRefundRules")
        group = log_group(self, "BookingLogs")
        lambda_role = iam.Role(
            self, "BookingRole", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        write_logs(lambda_role, group)
        function = lam.Function(
            self,
            "BookingApi",
            runtime=lam.Runtime.PYTHON_3_12,
            handler="common.public_booking.lambda_handler",
            code=lam.Code.from_asset(gateway_package()),
            role=lambda_role,
            log_group=group,
            timeout=Duration.seconds(5),
            reserved_concurrent_executions=2,
        )
        role = iam.Role(
            self,
            "GatewayRole",
            assumed_by=iam.ServicePrincipal(
                "bedrock-agentcore.amazonaws.com",
                conditions={
                    "StringEquals": {"aws:SourceAccount": self.account},
                    "ArnLike": {
                        "aws:SourceArn": (
                            f"arn:{self.partition}:bedrock-agentcore:{self.region}:"
                            f"{self.account}:gateway/*"
                        )
                    },
                },
            ),
        )
        # Gateway can invoke only this public quote function; it cannot mutate bookings or payments.
        role.add_to_policy(
            iam.PolicyStatement(
                actions=["lambda:InvokeFunction"], resources=[function.function_arn]
            )
        )
        gateway = ac.CfnGateway(
            self,
            "Gateway",
            name="nimbus-booking",
            role_arn=role.role_arn,
            authorizer_type="CUSTOM_JWT",
            authorizer_configuration={
                "customJwtAuthorizer": {
                    "discoveryUrl": (
                        f"https://cognito-idp.{self.region}.amazonaws.com/{pool.user_pool_id}"
                        "/.well-known/openid-configuration"
                    ),
                    "allowedClients": [app_client.user_pool_client_id],
                    "allowedScopes": ["nimbus/read"],
                }
            },
            protocol_type="MCP",
            protocol_configuration={"mcp": {"searchType": "SEMANTIC"}},
            policy_engine_configuration={"arn": engine.attr_policy_engine_arn, "mode": "ENFORCE"},
        )
        target = ac.CfnGatewayTarget(
            self,
            "BookingTarget",
            name="nimbus",
            gateway_identifier=gateway.attr_gateway_identifier,
            credential_provider_configurations=[{"credentialProviderType": "GATEWAY_IAM_ROLE"}],
            target_configuration={
                "mcp": {
                    "lambda": {
                        "lambdaArn": function.function_arn,
                        "toolSchema": {
                            "inlinePayload": [
                                {
                                    "name": "search_flights",
                                    "description": "Find public synthetic flight quotes",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {"destination": {"type": "string"}},
                                        "required": ["destination"],
                                    },
                                },
                                {
                                    "name": "refund_quote",
                                    "description": "Quote a refund; never issue money",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {"amount_cents": {"type": "integer"}},
                                        "required": ["amount_cents"],
                                    },
                                },
                            ]
                        },
                    }
                }
            },
        )
        gateway.node.add_dependency(role)
        for action, condition in [
            ("search_flights", ""),
            (
                "refund_quote",
                " when { context.input.amount_cents > 0 && context.input.amount_cents <= 50000 }",
            ),
        ]:
            policy = ac.CfnPolicy(
                self,
                action + "Policy",
                name="Permit" + action.replace("_", ""),
                policy_engine_id=engine.attr_policy_engine_id,
                validation_mode="FAIL_ON_ANY_FINDINGS",
                enforcement_mode="ACTIVE",
                definition={
                    "cedar": {
                        "statement": (
                            f'permit(principal, action == AgentCore::Action::"nimbus___{action}", '
                            f'resource == AgentCore::Gateway::"{gateway.attr_gateway_arn}")'
                            f"{condition};"
                        )
                    }
                },
            )
            policy.node.add_dependency(target)
        identity = ac.CfnWorkloadIdentity(
            self,
            "Identity",
            name="NimbusCopilot",
            allowed_resource_oauth2_return_urls=["http://localhost:8765/callback"],
        )
        traces = log_group(self, "ReviewedPublicTraces")
        results = log_group(self, "EvaluationResults")
        eval_role = iam.Role(
            self,
            "EvaluationRole",
            assumed_by=iam.ServicePrincipal(
                "bedrock-agentcore.amazonaws.com",
                conditions={"StringEquals": {"aws:SourceAccount": self.account}},
            ),
        )
        # Query only reviewed traces. Log enumeration/results APIs lack resource scoping.
        eval_role.add_to_policy(
            iam.PolicyStatement(actions=["logs:StartQuery"], resources=[traces.log_group_arn])
        )
        eval_role.add_to_policy(
            iam.PolicyStatement(
                actions=["logs:DescribeLogGroups", "logs:GetQueryResults"], resources=["*"]
            )
        )
        # Index only this group's fields, never modify account-wide Transaction Search settings.
        eval_role.add_to_policy(
            iam.PolicyStatement(
                actions=["logs:DescribeIndexPolicies", "logs:PutIndexPolicy"],
                resources=[traces.log_group_arn],
            )
        )
        write_logs(eval_role, results)
        online = ac.CfnOnlineEvaluationConfig(
            self,
            "OnlineEvaluation",
            online_evaluation_config_name="NimbusPublicQuality",
            evaluation_execution_role_arn=eval_role.role_arn,
            execution_status="DISABLED",
            rule={"samplingConfig": {"samplingPercentage": 1}},
            data_source_config={
                "cloudWatchLogs": {
                    "logGroupNames": [traces.log_group_name],
                    "serviceNames": ["nimbus-support"],
                }
            },
            evaluators=[{"evaluatorId": "Builtin.Helpfulness"}],
            output_config={"cloudWatchConfig": {"logGroupName": results.log_group_name}},
        )
        online.node.add_dependency(eval_role)
        trace_bucket = bucket(self, "ReviewedTraceExport", retention_days=1)
        job_role = iam.Role(
            self, "JobRole", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        job_logs = log_group(self, "JobLogs")
        write_logs(job_role, job_logs)
        # Only one reviewed object can be sent to the managed evaluator.
        job_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject"], resources=[trace_bucket.attr_arn + "/session-spans.json"]
            )
        )
        job_role.add_to_policy(
            iam.PolicyStatement(
                actions=["bedrock-agentcore:Evaluate"],
                resources=[
                    f"arn:{self.partition}:bedrock-agentcore:::evaluator/Builtin.Helpfulness"
                ],
            )
        )
        job = lam.DockerImageFunction(
            self,
            "ScheduledJudge",
            code=lam.DockerImageCode.from_image_asset(
                str(prepare("lambda")),
                platform=assets.Platform.LINUX_AMD64,
                cmd=["common.scheduled_evaluation.handler"],
            ),
            memory_size=1024,
            role=job_role,
            log_group=job_logs,
            timeout=Duration.seconds(60),
            reserved_concurrent_executions=1,
            environment={"TRACE_BUCKET": trace_bucket.ref},
        )
        schedule_role = iam.Role(
            self,
            "ScheduleRole",
            assumed_by=iam.ServicePrincipal(
                "scheduler.amazonaws.com",
                conditions={"StringEquals": {"aws:SourceAccount": self.account}},
            ),
        )
        # The scheduler can invoke only the bounded judge job, not arbitrary functions.
        schedule_role.add_to_policy(
            iam.PolicyStatement(actions=["lambda:InvokeFunction"], resources=[job.function_arn])
        )
        schedule = scheduler.CfnSchedule(
            self,
            "DailyQuality",
            flexible_time_window={"mode": "OFF"},
            schedule_expression="rate(1 day)",
            state=enabled.value_as_string,
            target={
                "arn": job.function_arn,
                "roleArn": schedule_role.role_arn,
                "retryPolicy": {"maximumRetryAttempts": 0, "maximumEventAgeInSeconds": 60},
            },
        )
        schedule.node.add_dependency(schedule_role)
        for key, value in {
            "MemoryId": memory.attr_memory_id,
            "GatewayUrl": gateway.attr_gateway_url,
            "GatewayArn": gateway.attr_gateway_arn,
            "UserPoolId": pool.user_pool_id,
            "ClientId": app_client.user_pool_client_id,
            "LoginDomain": domain.base_url(),
            "WorkloadIdentityArn": identity.attr_workload_identity_arn,
            "ReviewedTraceBucket": trace_bucket.ref,
            "TraceLogGroup": traces.log_group_name,
            "OnlineEvaluationId": online.attr_online_evaluation_config_id,
            "ScheduleName": schedule.ref,
        }.items():
            CfnOutput(self, key, value=value)
