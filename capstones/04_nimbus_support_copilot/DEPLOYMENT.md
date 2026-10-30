# Optional flagship deployment

**AWS required; billable and not executed during authoring.** The default capstone
is local. Read [production inventory and pricing](../../infra/PRODUCTION.md) and
[Guardrail setup](../../infra/13_guardrails/README.md) first. Use a dedicated learning
account, SSO profile, budget alert and a supported region. Docker must be running;
the Runtime image targets Linux ARM64.

## Deploy and connect the existing stacks

1. Follow the Module 21 guide to deploy `NimbusAgentCore`, keeping its evaluation
   schedule disabled. Record `MemoryId`, `GatewayUrl`, `UserPoolId` and `ClientId`.
2. Deploy `NimbusGuardrailLab`; record its Guardrail ID and published version.
3. Follow the Runtime guide to build and deploy `NimbusRuntime`. Pass the six
   outputs above as CDK parameters. They are resource identifiers, not secrets.

From the repository root, replace each uppercase value with the corresponding
stack output before running this one-line command on any supported shell:

```text
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk deploy NimbusRuntime --app "python infra/20_runtime/app.py" --profile nimbus-course --parameters MemoryId=MEMORY_ID_FROM_STACK --parameters GatewayUrl=GATEWAY_URL_FROM_STACK --parameters UserPoolId=USER_POOL_ID_FROM_STACK --parameters ClientId=CLIENT_ID_FROM_STACK --parameters GuardrailId=GUARDRAIL_ID_FROM_STACK --parameters GuardrailVersion=PUBLISHED_VERSION_FROM_STACK
```

The Runtime role receives CreateEvent/RetrieveMemoryRecords/DeleteEvent on that
single Memory resource, ApplyGuardrail on that single Guardrail, selected model
invocation, image pull and log-stream access. Gateway uses the traveler's JWT.
The extra Memory/Guardrail policy is absent when MemoryId is blank, preserving
the standalone policy-agent Runtime lesson. Supply all six parameters together.

Set `AGENTCORE_RUNTIME_ARN` locally from RuntimeArn. Complete the documented
Cognito browser sign-in and keep `NIMBUS_ACCESS_TOKEN` only in the process
environment. Never put the token in an image, commit, notebook, trace or prompt.

```text
uv run --all-groups python capstones/04_nimbus_support_copilot/solution/main.py --live-aws
```

The authenticated host sends one IAM-authorized Runtime request containing the
access token. The handler verifies its signature, issuer, expiry, client, scope
and token type before opening Gateway or accessing Memory. It then runs policy
retrieval, preference recall and a public flight quote through a Guardrail-bound
agent. The token is not exposed to the model or returned result. Do not enable
HTTP request-body logging. Offline ASGI, JWT-denial and real local MCP tests cover
this path; cloud IAM propagation and service behavior still require a live check.

The Memory lesson writes a **synthetic** preference event and deletes that event
in `finally`. Long-term extraction is asynchronous and may not return a new
preference immediately. Derived records can remain until the isolated Memory
resource is destroyed. Do not treat this as a real customer's consent workflow.

## Approval, evaluation and tracing

Run the local `--mock` workflow first; it uses the actual interrupt ledger and
Strands Evals. `--trace --mock` exports numeric spans for the composed local
workflow. `--guarded` demonstrates the configured Guardrail on the local approval
agent. The hosted service returns evidence and `approval_required: true`; the
trusted host owns durable approval. The course ledger mutates only synthetic
local records. No production payment endpoint or hosted supervisor interface is
implemented. A cloud quote cannot bypass that boundary.

Before a real release, run held-out cases against the selected live model,
inspect citations and denial behavior, and configure telemetry retention and
redaction. The default Runtime environment disables SDK telemetry; the local
OTLP lab is not evidence that a managed dashboard has been configured.

## Teardown

Stop any evaluation schedule and active managed tool sessions using the Module
21 guide. Delete Runtime first, then the AgentCore and Guardrail stacks:

```text
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk destroy NimbusRuntime --app "python infra/20_runtime/app.py" --profile nimbus-course
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk destroy NimbusAgentCore --app "python infra/21_agentcore/app.py" --profile nimbus-course
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk destroy NimbusGuardrailLab --app "python infra/13_guardrails/app.py" --profile nimbus-course
uv run python scripts/find_leftovers.py --regions us-east-1 --profile nimbus-course
```

Replace the scan region with every region you used. Follow the inventory for
retained trace objects, ECR images, logs and bootstrap assets. Destroying the
isolated Memory deletes the demo's derived records. Shared account bootstrap
resources are not automatically removed. A tag scan is supporting evidence,
not proof that an account has no billable resources.
