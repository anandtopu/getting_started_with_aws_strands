"""Small explicit CDK hosting stacks. Synthesizing never builds images or deploys AWS."""

from aws_cdk import CfnCondition, CfnOutput, CfnParameter, Duration, Fn, RemovalPolicy, Stack, Tags
from aws_cdk import aws_bedrockagentcore as ac
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr_assets as assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_secretsmanager as secrets
from aws_cdk import aws_ssm as ssm

from common.config import course_value
from common.infra_stacks import PROJECT
from scripts.prepare_deployment import prepare


def log_group(scope, name):
    return logs.LogGroup(
        scope, name, retention=logs.RetentionDays.ONE_WEEK, removal_policy=RemovalPolicy.DESTROY
    )


def write_logs(role, group):
    # The group is provisioned by CloudFormation; this role can write only its streams.
    role.add_to_policy(
        iam.PolicyStatement(
            actions=["logs:CreateLogStream", "logs:PutLogEvents"], resources=[group.log_group_arn]
        )
    )


def model_environment(scope, role):
    model = CfnParameter(scope, "ModelId", default=course_value("BEDROCK_MODEL_ID"))
    foundation = CfnParameter(
        scope, "FoundationModelId", default=course_value("BEDROCK_MODEL_ID").removeprefix("us.")
    )
    # Converse is authorized through these IAM actions; no raw per-model InvokeModel body is used.
    # Cross-region profiles need the selected foundation model in every routing destination.
    role.add_to_policy(
        iam.PolicyStatement(
            actions=["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
            resources=[
                f"arn:{scope.partition}:bedrock:{scope.region}:{scope.account}:inference-profile/{model.value_as_string}",
                *[
                    f"arn:{scope.partition}:bedrock:{region}::foundation-model/{foundation.value_as_string}"
                    for region in ("us-east-1", "us-east-2", "us-west-2")
                ],
            ],
        )
    )
    return {
        "MODEL_PROVIDER": "bedrock",
        "MODEL_ID": model.value_as_string,
        "MODEL_TEMPERATURE": "0",
        "MODEL_MAX_TOKENS": "512",
        "OTEL_SDK_DISABLED": "true",
    }


def pull_image(role, image):
    # ECR authorization tokens have no resource-level IAM support.
    role.add_to_policy(iam.PolicyStatement(actions=["ecr:GetAuthorizationToken"], resources=["*"]))
    # Download only this generated asset repository's images.
    role.add_to_policy(
        iam.PolicyStatement(
            actions=[
                "ecr:BatchGetImage",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchCheckLayerAvailability",
            ],
            resources=[image.repository.repository_arn],
        )
    )


class LambdaStack(Stack):
    def __init__(self, scope, name, **kwargs):
        super().__init__(scope, name, **kwargs)
        Tags.of(self).add("project", PROJECT)
        group = log_group(self, "SupportLogs")
        role = iam.Role(
            self, "SupportRole", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        write_logs(role, group)
        environment = model_environment(self, role)
        function = lam.DockerImageFunction(
            self,
            "Support",
            role=role,
            log_group=group,
            code=lam.DockerImageCode.from_image_asset(
                str(prepare("lambda")), platform=assets.Platform.LINUX_AMD64
            ),
            architecture=lam.Architecture.X86_64,
            memory_size=1024,
            timeout=Duration.seconds(35),
            reserved_concurrent_executions=2,
            environment=environment,
        )
        CfnOutput(self, "FunctionName", value=function.function_name)


class RuntimeStack(Stack):
    def __init__(self, scope, name, **kwargs):
        super().__init__(scope, name, **kwargs)
        Tags.of(self).add("project", PROJECT)
        image = assets.DockerImageAsset(
            self, "Image", directory=str(prepare("runtime")), platform=assets.Platform.LINUX_ARM64
        )
        role = iam.Role(
            self,
            "RuntimeRole",
            assumed_by=iam.ServicePrincipal(
                "bedrock-agentcore.amazonaws.com",
                conditions={
                    "StringEquals": {"aws:SourceAccount": self.account},
                    "ArnLike": {
                        "aws:SourceArn": (
                            f"arn:{self.partition}:bedrock-agentcore:{self.region}:"
                            f"{self.account}:runtime/*"
                        )
                    },
                },
            ),
        )
        pull_image(role, image)
        environment = model_environment(self, role)
        environment["AWS_REGION"] = self.region
        parameters = {}
        for key, variable in {
            "MemoryId": "AGENTCORE_MEMORY_ID",
            "GatewayUrl": "AGENTCORE_GATEWAY_URL",
            "UserPoolId": "NIMBUS_USER_POOL_ID",
            "ClientId": "NIMBUS_CLIENT_ID",
            "GuardrailId": "BEDROCK_GUARDRAIL_ID",
            "GuardrailVersion": "BEDROCK_GUARDRAIL_VERSION",
        }.items():
            parameter = CfnParameter(self, key, default="")
            parameters[key] = parameter.value_as_string
            environment[variable] = parameter.value_as_string
        enabled = CfnCondition(
            self,
            "CopilotConfigured",
            expression=Fn.condition_not(Fn.condition_equals(parameters["MemoryId"], "")),
        )
        # Temporary synthetic preference events and recall are limited to this configured memory.
        # Guardrail application is limited to the explicitly configured guardrail.
        policy = iam.CfnPolicy(
            self,
            "CopilotAccess",
            policy_name="NimbusRuntimeCopilot",
            roles=[role.role_name],
            policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "bedrock-agentcore:CreateEvent",
                            "bedrock-agentcore:RetrieveMemoryRecords",
                            "bedrock-agentcore:DeleteEvent",
                        ],
                        "Resource": [
                            f"arn:{self.partition}:bedrock-agentcore:{self.region}:"
                            f"{self.account}:memory/{parameters['MemoryId']}"
                        ],
                    },
                    {
                        "Effect": "Allow",
                        "Action": ["bedrock:ApplyGuardrail"],
                        "Resource": [
                            f"arn:{self.partition}:bedrock:{self.region}:"
                            f"{self.account}:guardrail/{parameters['GuardrailId']}"
                        ],
                    },
                ],
            },
        )
        policy.cfn_options.condition = enabled
        runtime = ac.CfnRuntime(
            self,
            "Runtime",
            agent_runtime_name="NimbusSupport",
            role_arn=role.role_arn,
            agent_runtime_artifact={"containerConfiguration": {"containerUri": image.image_uri}},
            network_configuration={"networkMode": "PUBLIC"},
            environment_variables=environment,
            lifecycle_configuration={"idleRuntimeSessionTimeout": 60, "maxLifetime": 900},
        )
        # Runtime's log name includes its generated ID; policy uses the known service prefix to
        # avoid a Role -> Runtime -> Role dependency cycle. No other log groups are writable.
        role.add_to_policy(
            iam.PolicyStatement(
                actions=["logs:CreateLogStream", "logs:PutLogEvents"],
                resources=[
                    f"arn:{self.partition}:logs:{self.region}:{self.account}:log-group:/aws/bedrock-agentcore/runtimes/*:*"
                ],
            )
        )
        logs.LogGroup(
            self,
            "RuntimeLogs",
            log_group_name=f"/aws/bedrock-agentcore/runtimes/{runtime.attr_agent_runtime_id}-DEFAULT",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )
        runtime.node.add_dependency(role)
        CfnOutput(self, "RuntimeArn", value=runtime.attr_agent_runtime_arn)


class FargateStack(Stack):
    @property
    def availability_zones(self):
        # Resolve zones in CloudFormation at deployment, without credentialed CDK lookups.
        return [Fn.select(index, Fn.get_azs()) for index in (0, 1)]

    def __init__(self, scope, name, **kwargs):
        super().__init__(scope, name, **kwargs)
        Tags.of(self).add("project", PROJECT)
        certificate = CfnParameter(
            self, "CertificateArn", description="Existing ACM certificate in this region"
        )
        allowed = CfnParameter(
            self, "AllowedCidr", description="Your workstation public IPv4 CIDR, e.g. a /32"
        )
        vpc = ec2.Vpc(
            self,
            "Vpc",
            availability_zones=self.availability_zones,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(name="Public", subnet_type=ec2.SubnetType.PUBLIC)
            ],
        )
        alb_sg = ec2.SecurityGroup(self, "AlbSecurity", vpc=vpc, allow_all_outbound=False)
        task_sg = ec2.SecurityGroup(self, "TaskSecurity", vpc=vpc)
        alb_sg.add_ingress_rule(ec2.Peer.ipv4(allowed.value_as_string), ec2.Port.tcp(443))
        alb_sg.add_egress_rule(task_sg, ec2.Port.tcp(8080))
        task_sg.add_ingress_rule(alb_sg, ec2.Port.tcp(8080))
        image = assets.DockerImageAsset(
            self, "Image", directory=str(prepare("fargate")), platform=assets.Platform.LINUX_AMD64
        )
        group = log_group(self, "ApiLogs")
        secret = secrets.Secret(
            self,
            "ApiToken",
            generate_secret_string=secrets.SecretStringGenerator(
                password_length=40, exclude_punctuation=True
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )
        parameter = ssm.StringParameter(self, "ServiceName", string_value="nimbus-support")
        execution = iam.Role(
            self, "ExecutionRole", assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        role = iam.Role(
            self, "TaskRole", assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        pull_image(execution, image)
        write_logs(execution, group)
        # The ECS agent injects this one credential; the LLM-facing role cannot retrieve secrets.
        execution.add_to_policy(
            iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue"], resources=[secret.secret_arn]
            )
        )
        # Read one service setting if the application opts into dynamic configuration.
        role.add_to_policy(
            iam.PolicyStatement(actions=["ssm:GetParameter"], resources=[parameter.parameter_arn])
        )
        environment = model_environment(self, role)
        environment["AWS_REGION"] = self.region
        task = ecs.CfnTaskDefinition(
            self,
            "Task",
            cpu="256",
            memory="512",
            network_mode="awsvpc",
            requires_compatibilities=["FARGATE"],
            execution_role_arn=execution.role_arn,
            task_role_arn=role.role_arn,
            container_definitions=[
                ecs.CfnTaskDefinition.ContainerDefinitionProperty(
                    name="support",
                    image=image.image_uri,
                    essential=True,
                    port_mappings=[ecs.CfnTaskDefinition.PortMappingProperty(container_port=8080)],
                    environment=[
                        ecs.CfnTaskDefinition.KeyValuePairProperty(name=k, value=v)
                        for k, v in environment.items()
                    ],
                    secrets=[
                        ecs.CfnTaskDefinition.SecretProperty(
                            name="NIMBUS_API_TOKEN", value_from=secret.secret_arn
                        )
                    ],
                    log_configuration=ecs.CfnTaskDefinition.LogConfigurationProperty(
                        log_driver="awslogs",
                        options={
                            "awslogs-group": group.log_group_name,
                            "awslogs-region": self.region,
                            "awslogs-stream-prefix": "support",
                        },
                    ),
                )
            ],
        )
        cluster = ecs.Cluster(self, "Cluster", vpc=vpc)
        balancer = elb.CfnLoadBalancer(
            self,
            "LoadBalancer",
            scheme="internet-facing",
            subnets=[s.subnet_id for s in vpc.public_subnets],
            security_groups=[alb_sg.security_group_id],
            load_balancer_attributes=[{"key": "idle_timeout.timeout_seconds", "value": "60"}],
        )
        target = elb.CfnTargetGroup(
            self,
            "Targets",
            port=8080,
            protocol="HTTP",
            target_type="ip",
            vpc_id=vpc.vpc_id,
            health_check_path="/health",
        )
        listener = elb.CfnListener(
            self,
            "Https",
            load_balancer_arn=balancer.ref,
            port=443,
            protocol="HTTPS",
            ssl_policy="ELBSecurityPolicy-TLS13-1-2-2021-06",
            certificates=[{"certificateArn": certificate.value_as_string}],
            default_actions=[{"type": "forward", "targetGroupArn": target.ref}],
        )
        service = ecs.CfnService(
            self,
            "Service",
            cluster=cluster.cluster_arn,
            task_definition=task.ref,
            desired_count=1,
            launch_type="FARGATE",
            deployment_configuration={
                "deploymentCircuitBreaker": {"enable": True, "rollback": True}
            },
            network_configuration={
                "awsvpcConfiguration": {
                    "assignPublicIp": "ENABLED",
                    "subnets": [s.subnet_id for s in vpc.public_subnets],
                    "securityGroups": [task_sg.security_group_id],
                }
            },
            load_balancers=[
                {"containerName": "support", "containerPort": 8080, "targetGroupArn": target.ref}
            ],
        )
        service.node.add_dependency(listener, execution, role)
        CfnOutput(self, "LoadBalancerDns", value=balancer.attr_dns_name)
        CfnOutput(self, "ApiTokenSecretArn", value=secret.secret_arn)
        CfnOutput(self, "ServiceParameter", value=parameter.parameter_name)
