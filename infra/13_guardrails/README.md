# Optional Bedrock Guardrails lab

**AWS required for deployment; offline synthesis costs $0.** This lab creates a
Bedrock Guardrail, a published version and a managed policy scoped to applying
that guardrail. It creates no compute, database or payment integration. Read the
[SSO, budget and region setup](../../docs/AWS_SETUP.md) first. Authoring checks
synthesize the template and stub service contracts; no AWS deployment is claimed.

## Inspect and deploy only if you choose the AWS branch

From the repository root, install Node.js 22+ and run:

```text
uv sync --group aws
npm ci --prefix infra
uv run --group aws python scripts/synth_all.py
```

[app.py](app.py) selects the stack, and [GuardrailStack](../../common/guardrail_stack.py)
defines content filters, an investment-advice denied topic, email/phone masking,
and grounding/relevance thresholds of 0.7. Review
`infra/13_guardrails/cdk.out/NimbusGuardrailLab.template.json`. Supported resources
are tagged `project=getting-started-with-aws-strands`; untaggable versions are
tracked through the tagged CloudFormation stack. The scoped apply policy grants
only `bedrock:ApplyGuardrail` on this guardrail ARN. Chat-model invocation requires
a separate model-scoped policy; the deployment role needs broader CloudFormation
permissions and must not be given to the agent.

The following command creates billable-use configuration in your selected account.
Use your configured named SSO profile and an existing authorized CDK bootstrap:

```text
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk deploy NimbusGuardrailLab --app "python infra/13_guardrails/app.py" --profile nimbus-course
uv run python scripts/tier2_lab.py NimbusGuardrailLab inspect
```

Copy GuardrailId and GuardrailVersion outputs into BEDROCK_GUARDRAIL_ID and
BEDROCK_GUARDRAIL_VERSION in `.env`; choose MODEL_PROVIDER=bedrock. These IDs are
not credentials. An authorized administrator can attach GuardrailPolicyArn to
the caller's role. Keep the AWS_REGION setting consistent with the deployment
and supported model/Guardrails region. Then run:

```text
uv run python modules/13_guardrails/examples/05_bedrock_guardrails.py
```

The shared model factory uses synchronous streaming filtering and enabled trace.
The example prints trace categories only, then separately calls ApplyGuardrail
with tagged source/query/answer content for grounding. Inspect the returned
action and assessments. A configured filter is not proof of classifier quality.
Changes to the draft guardrail do not automatically update a published version:
publish a new version (replace the version construct with a new logical ID),
review the output and update the application version deliberately.

## Costs before deployment

Planning assumptions checked October 29, 2026 against
[Bedrock pricing](https://aws.amazon.com/bedrock/pricing/): no hourly always-on
compute charge for this configuration; evaluations are charged by enabled filter
and text units. One text unit is up to 1,000 characters, rounded up. Content filters
and denied topics each list $0.15/1,000 text units, sensitive-information filters
$0.10/1,000, and contextual grounding $0.10/1,000. If all four meter exactly
1,000 units each, the combined planning amount is $0.50, plus model inference.
Grounding counts source, query and answer; repeated input/output checks and
rounding can increase billed units. This is not a flat per-request quote.
At 100 small requests with one unit per enabled filter, the illustrative filter
total is $0.05; size and separate assessments change that. Verify regional rates
and the actual enabled features before deployment. This stack does not enable
Automated Reasoning or deploy a supporting reasoning policy.

## Tear down and verify

Stop the lesson first and record the stack outputs, including the guardrail ID.
The shared helper retains its Tier 2 filename but accepts this explicitly listed
Tier 3 stack. Inspection is read-only; deletion requires both explicit flags:

```text
uv run python scripts/tier2_lab.py NimbusGuardrailLab inspect
uv run python scripts/tier2_lab.py NimbusGuardrailLab destroy --execute --confirm-stack NimbusGuardrailLab
uv run python scripts/find_leftovers.py
aws bedrock list-guardrails --profile nimbus-course --region us-east-1
aws cloudformation describe-stacks --stack-name NimbusGuardrailLab --profile nimbus-course --region us-east-1
```

Replace us-east-1 with the configured region. The helper verifies the project tag,
deletes the stack and waits for completion. Confirm the recorded guardrail ID is
absent and CloudFormation reports that the stack no longer exists; confirm the
managed policy ARN is also gone. Remove stale guardrail IDs from `.env`. The tag
scanner should report no remaining project resources in the selected region;
service-specific inventory is necessary because tagging APIs do not cover every
resource type. Check every region/account you used. Investigate AccessDenied,
pagination or stack-deletion failures instead of treating them as empty inventory.
CDK bootstrap resources are separate shared infrastructure; do not delete them as
part of this lab. Live teardown has not been tested in an AWS account.

## Reference

- [CloudFormation Guardrail properties](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-bedrock-guardrail.html)
- [Strands Guardrails integration](https://strandsagents.com/docs/user-guide/sdk/safety-security/guardrails/)
- [Offline template/attachment tests](../../tests/test_guardrail_infra.py)
