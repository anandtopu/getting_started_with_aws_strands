"""Inspect actual synthesized production policies and cost-control defaults."""

import pytest


@pytest.fixture(scope="module")
def templates(tmp_path_factory):
    cdk = pytest.importorskip("aws_cdk")
    from aws_cdk.assertions import Template

    from common.agentcore_stack import AgentCoreStack
    from common.hosting_stacks import FargateStack, LambdaStack, RuntimeStack
    from common.observability_stack import ObservabilityStack

    app = cdk.App(outdir=str(tmp_path_factory.mktemp("production-cdk")))
    env = cdk.Environment(account="111122223333", region="us-east-1")
    stacks = {
        cls.__name__: cls(app, cls.__name__, env=env)
        for cls in (ObservabilityStack, LambdaStack, FargateStack, RuntimeStack, AgentCoreStack)
    }
    return {name: Template.from_stack(stack).to_json() for name, stack in stacks.items()}


def resources(template, kind):
    return [v["Properties"] for v in template["Resources"].values() if v["Type"] == kind]


def test_gateway_identity_policy_and_memory(templates):
    template = templates["AgentCoreStack"]
    gateway = resources(template, "AWS::BedrockAgentCore::Gateway")[0]
    assert gateway["AuthorizerType"] == "CUSTOM_JWT"
    assert gateway["PolicyEngineConfiguration"]["Mode"] == "ENFORCE"
    assert gateway["ProtocolConfiguration"]["Mcp"]["SearchType"] == "SEMANTIC"
    assert gateway["AuthorizerConfiguration"]["CustomJWTAuthorizer"]["AllowedScopes"] == [
        "nimbus/read"
    ]
    policies = resources(template, "AWS::BedrockAgentCore::Policy")
    assert len(policies) == 2 and all(p["EnforcementMode"] == "ACTIVE" for p in policies)
    assert "50000" in str(policies)
    target = resources(template, "AWS::BedrockAgentCore::GatewayTarget")[0]
    tools = target["TargetConfiguration"]["Mcp"]["Lambda"]["ToolSchema"]["InlinePayload"]
    refund = next(tool for tool in tools if tool["Name"] == "refund_quote")
    schema = refund["InputSchema"]
    assert schema["Required"] == ["amount_cents"]
    assert set(schema["Properties"]) == {"amount_cents"}
    memory = resources(template, "AWS::BedrockAgentCore::Memory")[0]
    assert len(memory["MemoryStrategies"]) == 4
    assert "EpisodicMemoryStrategy" in str(memory)
    assert memory["EventExpiryDuration"] == 7


def test_flagship_runtime_permissions_are_resource_bound(templates):
    template = templates["RuntimeStack"]
    policy = template["Resources"]["CopilotAccess"]
    assert policy["Condition"] == "CopilotConfigured"
    statements = policy["Properties"]["PolicyDocument"]["Statement"]
    assert set(statements[0]["Action"]) == {
        "bedrock-agentcore:CreateEvent",
        "bedrock-agentcore:RetrieveMemoryRecords",
        "bedrock-agentcore:DeleteEvent",
    }
    assert "MemoryId" in str(statements[0]["Resource"])
    assert statements[1]["Action"] == ["bedrock:ApplyGuardrail"]
    assert "GuardrailId" in str(statements[1]["Resource"])


def test_managed_evaluations_start_disabled(templates):
    template = templates["AgentCoreStack"]
    online = resources(template, "AWS::BedrockAgentCore::OnlineEvaluationConfig")[0]
    assert online["ExecutionStatus"] == "DISABLED"
    assert online["Rule"]["SamplingConfig"]["SamplingPercentage"] == 1
    schedule = resources(template, "AWS::Scheduler::Schedule")[0]
    assert schedule["ScheduleExpression"] == "rate(1 day)"
    assert template["Parameters"][schedule["State"]["Ref"]]["Default"] == "DISABLED"
    assert schedule["Target"]["RetryPolicy"]["MaximumRetryAttempts"] == 0
    functions = resources(template, "AWS::Lambda::Function")
    assert any(f.get("PackageType") == "Image" for f in functions)
    statements = [
        statement
        for policy in resources(template, "AWS::IAM::Policy")
        for statement in policy["PolicyDocument"]["Statement"]
        if "bedrock-agentcore:Evaluate" in str(statement.get("Action"))
    ]
    assert len(statements) == 1
    assert ":bedrock-agentcore:::evaluator/Builtin.Helpfulness" in str(statements[0]["Resource"])


def test_fargate_https_only_and_no_nat(templates):
    template = templates["FargateStack"]
    assert not resources(template, "AWS::EC2::NatGateway")
    listeners = resources(template, "AWS::ElasticLoadBalancingV2::Listener")
    assert len(listeners) == 1 and listeners[0]["Protocol"] == "HTTPS"
    assert listeners[0]["Port"] == 443
    task = resources(template, "AWS::ECS::TaskDefinition")[0]
    container = task["ContainerDefinitions"][0]
    assert task["Cpu"] == "256" and task["Memory"] == "512"
    assert container["Secrets"][0]["Name"] == "NIMBUS_API_TOKEN"
    assert "AWS_PROFILE" not in str(container["Environment"])


def test_no_wildcard_actions_and_retention(templates):
    for template in templates.values():
        # The repository-wide contract separately rejects wildcard IAM actions.
        for group in resources(template, "AWS::Logs::LogGroup"):
            assert group["RetentionInDays"] == 7
    runtime = resources(templates["RuntimeStack"], "AWS::BedrockAgentCore::Runtime")[0]
    assert "AWS_PROFILE" not in runtime["EnvironmentVariables"]
    assert runtime["LifecycleConfiguration"]["IdleRuntimeSessionTimeout"] == 60
