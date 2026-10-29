# Production labs: review, deploy deliberately, and delete

These are **optional AWS labs**. Authoring checks synthesize templates and run offline
contracts; no AWS deployment was performed. Complete [SSO and budget setup](../docs/AWS_SETUP.md)
first. Use an isolated learning account, choose a region supported by every selected service,
and read the dated [resource cost inventory](../docs/PRODUCTION_COSTS.md).

## Inventory and local validation

| App | Stack | Resources |
|---|---|---|
| [19_observability](19_observability/app.py) | NimbusObservability | Seven-day log group, latency alarm, scoped telemetry managed policy |
| [20_lambda](20_lambda/app.py) | NimbusLambda | Support image Lambda, role, seven-day logs |
| [20_runtime](20_runtime/app.py) | NimbusRuntime | ARM64 container Runtime, execution role, seven-day logs |
| [20_fargate](20_fargate/app.py) | NimbusFargate | VPC/two public subnets/routes/Internet gateway, security groups, ECS cluster/task/service, HTTPS ALB/listener/target group, role pair, secret, SSM parameter, logs |
| [21_agentcore](21_agentcore/app.py) | NimbusAgentCore | Four-strategy Memory, Cognito pool/client/scope/domain, workload identity, Gateway/Lambda target, Policy engine/two policies, booking Lambda, logs, disabled online evaluation, S3 export bucket, scheduled judge Lambda and disabled daily schedule |

Taggable resources carry `project=getting-started-with-aws-strands`; untaggable child
resources are owned by the tagged CloudFormation stack. No wildcard IAM actions are used.
Permission comments explain the few wildcard **resources** needed for APIs such as ECR
authorization and CloudWatch metrics. Containers hold no local credential files.

```text
uv sync --all-groups
npm ci --prefix infra
uv run --all-groups python scripts/synth_all.py
uv run --all-groups pytest tests/test_production.py
uv run --all-groups python scripts/prepare_deployment.py
```

Review `infra/<app>/cdk.out/*.template.json`, roles, trust conditions, tags, retention and
asset manifests. Synthesis uses a fictional account and disables credentialed context
lookups. It does not build Docker images, establish service access, prove deployment succeeds
or verify teardown. The Fargate template resolves availability zones during CloudFormation
deployment. You need at least two supported zones in the selected region.

Container dependencies are an exported subset of `uv.lock`. To refresh after an intentional
dependency update, run `uv export --frozen --only-group deploy --no-emit-project --output-file deploy/requirements.txt`.
Build the three contexts using the commands in [Module 20](../modules/20_deployment/README.md).
Record the pulled base-image digest, scan the result and test each image before a release.
Runtime needs an ARM64 build; an x86 workstation needs Docker buildx/emulation support.
The authoring machine's Docker engine was unavailable, so image builds are an outstanding check.

## Optional deployment

These commands **create billable resources**. Run only the stack you intend to use after
reviewing its template. An account administrator must provide CDK bootstrap asset storage
and a deployment role if not already present. Bootstrap is separate shared infrastructure.
All commands work as single lines in PowerShell and POSIX shells.

```text
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk deploy NimbusObservability --app "python infra/19_observability/app.py" --profile nimbus-course
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk deploy NimbusLambda --app "python infra/20_lambda/app.py" --profile nimbus-course
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk deploy NimbusRuntime --app "python infra/20_runtime/app.py" --profile nimbus-course
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk deploy NimbusAgentCore --app "python infra/21_agentcore/app.py" --profile nimbus-course
```

For Fargate, the deployment additionally requires `CertificateArn` and `AllowedCidr`.
Supply the ARN of your existing same-region ACM certificate and your workstation's public
IPv4 `/32` through CDK's `--parameters CertificateArn=... --parameters AllowedCidr=...` options.
Those ellipses are parameter notation, not a command to paste. Then use this base command
with the two actual parameter values appended:

```text
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk deploy NimbusFargate --app "python infra/20_fargate/app.py" --profile nimbus-course
```

Point the certificate's hostname to the output ALB DNS name using DNS you control. The ALB
has only HTTPS on port 443; testing its raw AWS DNS name will fail certificate hostname
validation. Fetch the bearer secret through an authorized human/application role and pass
it as an Authorization header, never as a URL query or prompt. Test anonymous denial,
oversized/malformed input, successful SSE completion and a failed stream. The demo bearer
is shared; per-user authorization and secret rotation are necessary for a real service.

The default model role permits the selected US inference profile and the matching foundation
model in `us-east-1`, `us-east-2` and `us-west-2`. For another profile, change both model
parameters and the allowed routing destinations. Confirm regional model lifecycle/access
before deployment. Synthesis cannot determine your model entitlement or inference quotas.

## Invoke and compare

Copy nonsecret stack outputs into `.env`:

| Output | Setting |
|---|---|
| FunctionName | NIMBUS_LAMBDA_NAME |
| RuntimeArn | AGENTCORE_RUNTIME_ARN |
| MemoryId | AGENTCORE_MEMORY_ID |
| GatewayUrl | AGENTCORE_GATEWAY_URL |
| UserPoolId / ClientId / LoginDomain | NIMBUS_USER_POOL_ID / NIMBUS_CLIENT_ID / NIMBUS_LOGIN_DOMAIN |
| ServiceParameter / ApiTokenSecretArn | NIMBUS_SERVICE_PARAMETER / NIMBUS_API_SECRET_ARN |

The caller's SSO role needs only the operations it performs, scoped to these resources:
Lambda InvokeFunction; Runtime InvokeAgentRuntime; Memory CreateEvent, RetrieveMemoryRecords
and DeleteEvent; optional SSM GetParameter and SecretsManager GetSecretValue. These caller
permissions are distinct from the service execution roles deployed by CDK. Ask the account
administrator to bind them to the learning role; do not attach broad administrator policies.
Gateway verifies Cognito JWTs separately. A shared backend must also enforce tenant boundaries
on every data access; the course only uses synthetic public records.

```text
uv run --all-groups python modules/20_deployment/use_case/deployment_comparison.py --live-aws
```

Record warm and cold runs separately, confirm the answers cite policy evidence, and compare
distributions rather than one timestamp. The Runtime client creates a new UUID per invocation;
its session id is reported for later diagnostics. This stateless app does not restore earlier
conversation messages. Its 60-second idle/900-second maximum lifetime bounds abandoned
sessions; destroy the runtime after the lab. Deployment does not establish load capacity.

## Sign in to the Copilot

The stack creates a Cognito public app client with authorization-code flow, `openid` and
`nimbus/read`, and callback `http://localhost:8765/callback`. Self-registration is disabled.
Have the learning-account administrator create a course user in the pool and complete the
required first-password flow. No real traveler identity is needed.

```text
uv run --group identity python scripts/cognito_copilot.py
```

This opens Cognito's hosted sign-in page, uses PKCE (a one-use proof tying the code to this
client), validates callback state, exchanges the authorization code and launches the live
Copilot with the access token only in the child process environment. It does not save or print
the token. Port 8765 must be free. The Copilot verifies issuer, signature, expiry, client and
scope before binding Memory's actor to the verified subject. Sign out of the hosted page
and stop the process when finished. Do not manually paste tokens into committed files.

Outbound OAuth in example 03 is optional and needs a real partner OAuth registration and
AgentCore credential provider named by `NIMBUS_OAUTH_PROVIDER`. Configure its client secret
through the provider's protected secret workflow, allow only the required `read` scope and
configure the callback for that partner. `consent_required=True` means the host UI must finish
federation; it is not a successful authenticated API call. The course's public booking API
needs no third-party OAuth registration. See [Identity's official guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html).

## Policy and tool sessions

Test USD 500 and USD 500.01 through example 07 with a valid access token supplied by your
trusted host. Confirm both the client result **and the Gateway policy decision**. The deployed
Cedar engine uses `ENFORCE`; policies use `ACTIVE`. The Lambda retains its own integer-cents
check. Mock MCP tests exercise that local defense, not the AWS Cedar engine.

Code Interpreter and Browser use built-in resources, not custom long-lived tool definitions.
The caller needs the corresponding Start/Stop session and InvokeCodeInterpreter or
ConnectBrowserAutomationStream permissions scoped to the chosen tool identifier/session.
Both examples set 60-second sessions and stop in `finally`. After an interrupted live run,
list the active sessions in the AgentCore console and stop any remaining course session.
This live cleanup has not been exercised during authoring. The browser reads only fixed
synthetic HTML; the code tool runs only a reviewed sum. There is no real payment operation.

## CloudWatch, traces and managed evaluations

`NimbusObservability` provides a scoped metrics policy, seven-day log retention and an alarm.
Attach its policy only to the intended telemetry caller. The runtime examples disable SDK
telemetry by default; basic platform request logs are different from a complete model trace.
The local exporter projects numeric usage and is intentionally unsuitable for semantic judges.

The same projection can be exported directly to AWS's authenticated OTLP endpoint after
attaching the telemetry policy and reviewing the account's trace settings:

```text
uv run --group observability python -m common.telemetry_lab --cloud
```

This explicitly billable command signs protobuf requests with short-lived SSO/role
credentials and the `xray:PutTraceSegments` permission. It never sends private span content.
The [AWS OTLP endpoint contract](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-OTLPEndpoint.html)
uses HTTP and SigV4. Local tests check signing and rejection handling; live delivery remains
unverified. This is a basic trace export, not complete managed GenAI dashboard instrumentation.

Full AgentCore Observability requires supported instrumentation, trace delivery and account
Transaction Search configuration. Follow the current [telemetry delivery guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-configure.html)
and [evaluation prerequisites](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations-prerequisites.html)
in the isolated account. These account-wide settings can affect other workloads and have
their own costs; this stack does not silently change them. Export only a reviewed synthetic
session using [the documented CloudWatch query](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/getting-started-on-demand.html).
Keep the native `sessionSpans` records together for one session; do not substitute the tiny
Stubber fixture as real judge input.

```text
uv run --all-groups python modules/21_agentcore/examples/08_evaluations.py --live-aws --spans .nimbus/reviewed-session.json
```

Inspect every returned score and failure. A managed judgment is not automatically trustworthy:
compare it with a human rating. The `NimbusAgentCore` stack provides two distinct mechanisms:

- Online evaluation samples 1% of new traces in its dedicated reviewed public group. It is
  initially disabled. Configure valid supported trace delivery before enabling it through
  the service control plane; disable it before cleanup. It is continuous sampling, not a timer.
- The actual EventBridge daily schedule invokes a Lambda that reads only `session-spans.json`
  from the output `ReviewedTraceBucket`, calls Builtin.Helpfulness and rejects incomplete
  results or scores below 0.8. Upload a reviewed export to that exact key using the AWS CLI
  or S3 console, then test the judge Lambda once. Only then redeploy `NimbusAgentCore` with
  `--parameters EvaluationScheduleState=ENABLED`. The export expires after one day: refresh
  it deliberately for further runs. No automatic harvesting of production conversations occurs.

The schedule starts disabled and has zero retry attempts. Lambda errors/logs are the quality
failure signal; this course does not configure an email notification. Enable a reviewed alarm
or alert destination before depending on unattended operation. Disable with a redeploy using
`--parameters EvaluationScheduleState=DISABLED`. Do not enable online and scheduled evaluation
unnecessarily; each creates its own usage charges.

The scheduled judge uses the same hash-locked Lambda image dependency set as the support
handler, so its Evaluate API does not depend on the SDK bundled in Lambda's base runtime.

## Delete and verify

First disable online evaluation and the daily schedule. Stop managed browser/interpreter
sessions. Empty the isolated reviewed-export bucket (including any objects added manually).
Destroy only stacks you created:

```text
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk destroy NimbusAgentCore --app "python infra/21_agentcore/app.py" --profile nimbus-course
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk destroy NimbusFargate --app "python infra/20_fargate/app.py" --profile nimbus-course
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk destroy NimbusRuntime --app "python infra/20_runtime/app.py" --profile nimbus-course
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk destroy NimbusLambda --app "python infra/20_lambda/app.py" --profile nimbus-course
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk destroy NimbusObservability --app "python infra/19_observability/app.py" --profile nimbus-course
uv run python scripts/find_leftovers.py
```

Do not delete shared CDK bootstrap repositories/buckets wholesale. Inspect their course asset
images/objects and remove only items no active stack uses. Inspect retained or failed-delete
CloudFormation resources, Cognito user data, extracted Memory records, Gateway targets,
OAuth credential providers created separately, secrets, log groups, network interfaces and
all deployed regions. The tagging API does not list every resource type or built-in active
session. Confirm the console and stack deletion status as well. Check billing again after its
normal reporting delay. No assertion of a clean live account was made during authoring.
