"""Optional Guardrails configuration and least-privilege application policy."""

from aws_cdk import CfnOutput, Stack, Tags
from aws_cdk import aws_bedrock as bedrock
from aws_cdk import aws_iam as iam


class GuardrailStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        Tags.of(self).add("project", "getting-started-with-aws-strands")
        guardrail = bedrock.CfnGuardrail(
            self,
            "SupportGuardrail",
            name="nimbus-support-guardrail",
            blocked_input_messaging="This request is outside Nimbus support policy.",
            blocked_outputs_messaging="The response could not be verified safely.",
            content_policy_config={
                "filtersConfig": [
                    {"type": kind, "inputStrength": "MEDIUM", "outputStrength": "MEDIUM"}
                    for kind in ["HATE", "INSULTS", "SEXUAL", "VIOLENCE", "MISCONDUCT"]
                ]
            },
            topic_policy_config={
                "topicsConfig": [
                    {
                        "name": "InvestmentAdvice",
                        "type": "DENY",
                        "definition": "Personalized advice to buy or sell financial investments.",
                        "examples": ["Which stock should I buy today?"],
                    }
                ]
            },
            sensitive_information_policy_config={
                "piiEntitiesConfig": [
                    {"type": "EMAIL", "action": "ANONYMIZE"},
                    {"type": "PHONE", "action": "ANONYMIZE"},
                ]
            },
            contextual_grounding_policy_config={
                "filtersConfig": [
                    {"type": "GROUNDING", "threshold": 0.7},
                    {"type": "RELEVANCE", "threshold": 0.7},
                ]
            },
        )
        version = bedrock.CfnGuardrailVersion(
            self,
            "PublishedVersion",
            guardrail_identifier=guardrail.attr_guardrail_id,
            description="Nimbus teaching baseline",
        )
        # Application callers can apply only this guardrail; model inference is granted separately.
        policy = iam.ManagedPolicy(
            self,
            "ApplyGuardrailAccess",
            statements=[
                iam.PolicyStatement(
                    actions=["bedrock:ApplyGuardrail"], resources=[guardrail.attr_guardrail_arn]
                )
            ],
        )
        CfnOutput(self, "GuardrailId", value=guardrail.attr_guardrail_id)
        CfnOutput(self, "GuardrailVersion", value=version.attr_version)
        CfnOutput(self, "GuardrailArn", value=guardrail.attr_guardrail_arn)
        CfnOutput(self, "GuardrailPolicyArn", value=policy.managed_policy_arn)
