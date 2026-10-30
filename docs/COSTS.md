# Costs and cleanup

Planning date: **October 29, 2026**. Currency: USD, before tax. Region: `us-east-1` unless the selected service says otherwise. These are workload estimates, not measured invoices or spending limits. Later phases must replace planning assumptions with the delivered example's token counts and resource inventory.

The default tests, data generation and all Tier 1 mock runs cost **$0 in cloud charges**. Ollama has no hosted-model charge; electricity, hardware and downloads still have costs. Installing Python dependencies requires network access.

## Calculate inference cost

For uncached text inference:

```text
cost = input_tokens / 1,000,000 * input_price
     + output_tokens / 1,000,000 * output_price
```

Count **all** agent turns, including repeated conversation history, tool results, retries and model judges. Image, audio, caching, batch and regional rates may differ. Temperature zero does not guarantee identical output. Reasoning tokens may add output charges.

The planning rate for Nova 2 Lite is **$0.30 input / $2.50 output per million tokens**, as used in this [AWS worked example](https://aws.amazon.com/blogs/big-data/build-rag-ready-indexes-from-amazon-s3-with-amazon-opensearch-intelligent-ingestion/). Confirm the chosen deployment mode on the [Bedrock pricing page](https://aws.amazon.com/bedrock/pricing/) before running. A planning call of 2,000 input and 500 output tokens costs **$0.00185**. Ten such calls cost $0.0185. This deliberately includes more output than the short foundation demo normally needs.

Set `MODEL_INPUT_USD_PER_MILLION=0.30` and `MODEL_OUTPUT_USD_PER_MILLION=2.50` in `.env` only after confirming those rates for your model. The display reports an unknown hosted price when rates are absent; it never silently labels an unpriced cloud call free. Change both values when changing provider. [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) and [Claude model prices](https://platform.claude.com/docs/en/models/overview) have their own rates and conditions.

## Every module's planning allowance

The call counts below budget one pass through examples and a small exercise attempt. Each call uses the 2,000/500-token assumption above; output ceilings and retry limits must be checked in the eventual lesson. Optional services are **additional** to this table. No future module has been live-benchmarked.

| Module | Calls | Nova text estimate | Additional branch costs |
|---|---:|---:|---|
| 00 Setup | 5 | $0.0093 | Budget monitoring/email free; no Budget Actions |
| 01 First agent | 10 | $0.0185 | None |
| 02 Providers | 15 | $0.0278 | Other providers use their own prices |
| 03 Conversations and images | 15 | $0.0278 | Image token counts vary; this is text-only |
| 04 Structured output | 40 | $0.0740 | Includes the 20-ticket run; repair attempts can increase usage |
| 05 Building tools | 40 | $0.0740 | Includes tool continuations and checkpoint; local tools free |
| 06 Community tools | 20 | $0.0370 | Optional remote APIs priced separately |
| 07 RAG | 20 | $0.0370 | Local embeddings free; hosted embeddings extra |
| 08 Advanced RAG | 30 | $0.0555 | Optional Knowledge Base/vector storage, reranking |
| 09 Memory | 20 | $0.0370 | Optional S3/AgentCore/hosted memory |
| 10 Streaming | 15 | $0.0278 | None for local application hosting |
| 11 Hooks | 15 | $0.0278 | None |
| 12 Approvals | 20 | $0.0370 | Interrupted/repeated turns consume tokens |
| 13 Safety | 25 | $0.0463 | Optional Bedrock Guardrails policy checks |
| 14 MCP | 25 | $0.0463 | Server-specific API charges |
| 15 Agents as tools | 30 | $0.0555 | All child calls count |
| 16 Swarms | 40 | $0.0740 | Set iteration and token limits |
| 17 Graphs | 40 | $0.0740 | Parallel branches multiply usage |
| 18 A2A | 30 | $0.0555 | Remote partner hosting if enabled |
| 19 Observability and evaluation | 60 | $0.1110 | Model judges, trace storage and logging |
| 20 Deployment | 30 | $0.0555 | Lambda/Fargate/Runtime, networking, logs, images |
| 21 AgentCore | 50 | $0.0925 | Service charges listed below |
| B1 Voice | Not text-equivalent | Price separately | Audio input/output and active sessions |
| B2 TypeScript | 15 | $0.0278 | None locally |
| B3 Self-extending agents | 20 | $0.0370 | Isolated execution if hosted |
| B4 New features | 25 | $0.0463 | Depends on the confirmed feature set |

The 22 core modules total 550 planning calls, approximately **$1.02 in text inference**. This excludes optional AWS services, repeats, larger contexts and all capstones. Budgeting $5–$10 for exploratory text work leaves room for retries but is not a guarantee. A 100-call capstone experiment at the same token sizes adds $0.185; real RAG/crew capstones often use larger contexts. Audio needs a separate estimate when B1 is implemented.

## Hosted infrastructure changes the bill

Recheck each region and service generation before deployment. The [AgentCore price sheet](https://aws.amazon.com/bedrock/agentcore/pricing/) currently lists Runtime v1 at $0.0895/vCPU-hour and $0.00945/GB-hour; v2 at $0.1276 and $0.0169 respectively. Memory allocation and idle-session behavior matter. Gateway tool calls start at $0.005/1,000 calls; search, indexing and model inference are separate. Short-term memory pricing is volume-based: $1/GB ingested, $0.20/GB retrieved and $0.10/GB-month stored. Long-term memory, evaluation, identity and policy have separate meters. Do not use the retired event-count estimate for short-term memory.

For illustration, **0.25 active vCPU-hour and 0.25 GB-hour** at Runtime v1 rates cost about $0.0247 before inference/logging. This is a unit-cost calculation, not a promised runtime footprint. Resource sizes and retained sessions must be measured in the deployment lesson.

An [Application Load Balancer](https://aws.amazon.com/elasticloadbalancing/pricing/) in the US-East example is $0.0225/hour plus capacity charges, so even before traffic it is about $16.20 for 720 hours. [Fargate](https://aws.amazon.com/fargate/pricing/) compute, public IPv4 addresses, NAT gateways and outbound data can add substantially more. Destroy a practice deployment the same day; do not leave a load balancer running for a month to save a few token cents.

Use these official pages for optional components: [Lambda](https://aws.amazon.com/lambda/pricing/), [S3 and S3 Vectors](https://aws.amazon.com/s3/pricing/), [DynamoDB](https://aws.amazon.com/dynamodb/pricing/), [CloudWatch](https://aws.amazon.com/cloudwatch/pricing/), [ECR](https://aws.amazon.com/ecr/pricing/), [VPC/networking](https://aws.amazon.com/vpc/pricing/), and [Bedrock Guardrails/Knowledge Bases](https://aws.amazon.com/bedrock/pricing/). Do not assume a free tier, trial credits or a universally cheapest vector store. Each later infrastructure lesson must provide a concrete region, duration, request/storage allowance and calculator estimate before a deployment command is offered.

## Budget before billing

Follow [AWS setup](AWS_SETUP.md) to create a $10 monthly account-wide budget with 50%, 80% and 100% alerts. [Budget monitoring and notifications](https://aws.amazon.com/aws-cost-management/aws-budgets/pricing/) are free; Budget Actions and reports have separate pricing. This course's helper enables neither. Alerts can arrive after usage has occurred and cannot enforce a hard cap. Review the account's other workloads before choosing this amount.

## Teardown checklist

Phase 2 deploys nothing. A learner who creates the optional budget can remove only that budget with `uv run python scripts/budget.py --delete`; retaining it for later lessons is useful. For future resource-creating lessons:

1. Stop running clients, streaming requests, browser/code sessions and evaluation schedules.
2. Run that lesson's explicit teardown command against its recorded account and region.
3. Confirm the stack/resource deletion finishes; investigate `DELETE_FAILED` and retained resources.
4. Check S3 objects/versions, vector indexes, ECR images, CloudWatch logs, databases and memory stores against the lesson inventory. Empty only resources that belong to this course before deleting them.
5. Check regional networking charges, load balancers, NAT gateways and public IPs. Inspect global resources and budgets separately.
6. Run the read-only leftover inventory in **every region used**:

```text
uv run python scripts/find_leftovers.py --regions us-east-1 us-east-2 us-west-2
```

The helper paginates tagged-resource results and active tagged CloudFormation stacks, including stack children. Exit code **0** means no resources found within that scope, **1** means resources remain, and **2** means the scan was incomplete or failed. Permission failures are reported, never treated as proof of cleanup. Untagged resources, unsupported services, global resources, deleted-stack remnants and unlisted regions need separate review. Service-specific scanners arrive with their infrastructure lessons.

7. Review AWS Billing after its usage data refreshes. Keep the budget alert until you have checked for continued charges. Log out with `aws sso logout` when finished. Do not delete a shared CDK bootstrap stack or shared identity resources without the account owner's agreement.

Local `.nimbus/` contains only generated working state. Delete selected session/report directories when you no longer need them; keep committed `data/` for reproducible exercises.

## Delivered Tier 1 cost controls

All 37 examples and seven use cases have offline replay. Module 04 reports aggregate tokens for the 20-ticket evaluation; its three-turn per-ticket limit permits up to 60 calls if repairs are needed. Module 02 compares six prompts across three providers and reports unknown prices rather than assigning one provider's rate to another. The checkpoint bounds the conversation to seven turns. These are call budgets, not dollar caps.

Direct tool demonstrations such as workspace editing and AWS Stubber discovery use no model calls. Cache and image costs cannot be predicted accurately from text length alone. No live model bills were measured. All Tier 1 modules create zero AWS resources; temporary tool files are removed automatically and reports remain under ignored `.nimbus/`.

## Delivered Tier 2 cost controls

All 18 new examples, three use cases and the checkpoint have offline replay. Local Chroma, SQLite and file sessions create no AWS resources. Live local retrieval requires an Ollama embedding-model download. The optional `--judge-answers` comparison generates and judges 12 answers: at most 72 model turns (four for each answer, two for each judge), with actual token charges determined by the configured provider. Retrieval scores alone make no chat-model calls; live Ollama embeddings use local compute.

The [optional lab inventory and estimates](../infra/README.md#dated-cost-assumptions-october-29-2026) cover S3 Vectors/Knowledge Bases, S3 sessions and AgentCore Memory, with explicit small-workload assumptions. They incorporate the October 2026 AgentCore consumption-based memory pricing change and avoid claiming that any vector store is universally cheapest. Reranking has a separate Bedrock charge; removing `--mock` from the reranking example opts into that AWS operation. No paid usage was measured.

Use the [tag-checked teardown helper](../scripts/tier2_lab.py) and [service-specific leftover checks](../infra/README.md#tear-down-and-verify) for these labs. Inspect is the default action; deletion requires both execution and exact-stack confirmation flags. Cloud cleanup has offline tests but has not been exercised against an AWS account.

## Delivered Tier 3 cost controls

Modules 10–14 have offline replay and local tools at $0 hosted cost. Module 10
caps independent concurrent agents and wall time; modules 11–13 enforce tool and
turn budgets. Small hosted experiments retain the $0.05–$0.20 planning envelope,
not a spending guarantee. Actual token rates come from the selected model.
Streaming alone does not reduce token cost. Failed, cancelled and repeated calls
may still incur provider charges.

The [Guardrails lab cost table](../infra/13_guardrails/README.md#costs-before-deployment)
prices content, topics, PII and grounding with October 29, 2026 assumptions.
Grounding includes source/query/answer text; configuration does not run always-on
compute. The default MCP booking servers use disposable SQLite data and no cloud.
AWS Documentation/Pricing MCP branches need network setup; Pricing uses read-only
SSO access. Its $1.87 Lambda arithmetic is explicitly illustrative and excludes
free tier, logs, transfer and other services, not an actual bill forecast.

Stop local web servers, inspect persisted synthetic approval state, and follow
the [Guardrails teardown](../infra/13_guardrails/README.md#tear-down-and-verify)
if you chose to deploy that optional stack. No cloud deployment/cleanup was tested.

## Delivered Tier 4 cost controls

Modules 15–18 create no AWS resources. Offline replay costs $0; Ollama has no hosted
API fee. Bedrock inference uses the selected model's dated rates and default 512-token
response ceiling. More agents can increase total input history and model calls even
when parallel execution reduces elapsed time.

The single-agent comparison makes two fixture calls (240 synthetic tokens); the
delegated version makes five (600). The normal four-node swarm makes seven (840).
The approved checkpoint makes five (600), including both search specialists. These
are accounting tests, not live token forecasts. Configured rates yield an inference
estimate; absent rates remain unknown. Revisited Swarm nodes have a pinned-SDK
cumulative-usage caveat, so those reports suppress dollar estimates. Remote A2A
provider usage is unavailable in the response and must not be counted as zero.

Each child has a three-turn budget; delegated tools are limited to one attempt per
role. Swarms and graphs limit visits and node waiting. Swarm execution_timeout checks
between nodes; a host asyncio.timeout is needed for a strict whole-call deadline.
Cancellation does not reverse completed remote actions or necessarily stop billing.
The course's partner service only quotes synthetic upgrades. Its loopback process
and temporary token are closed after each example. No cloud teardown is required.

## Delivered Tier 5 cost controls

The [production cost inventory](PRODUCTION_COSTS.md) prices each added resource, separates always-running Fargate/ALB/IPv4 costs from usage-based hosting, and records the October 2026 Memory pricing change. Managed evaluations start disabled; tools have short session lifetimes; logs have seven-day retention. Follow [the production cleanup sequence](../infra/PRODUCTION.md).

## Bonus modules and capstones

All bonus and capstone `--mock` runs cost $0 in AWS/model charges. TypeScript uses the same token accounting assumptions as the first agent; B3 adds proposal and validation calls; B4 red-team cases multiply model calls. B1 live voice uses audio-token pricing and an isolated adapter environment: consult [Nova pricing](https://aws.amazon.com/bedrock/pricing/) for the selected model and region before a session.

CloudOps performs read-only MCP reference queries; its reports show synthetic spend, not account savings. Trip Crew uses four bounded specialist agents and the free Open-Meteo endpoint. Document extraction uses image/model tokens plus optional [DynamoDB requests and storage](../infra/document_pipeline/README.md). The flagship combines [production resource costs](PRODUCTION_COSTS.md) and Guardrail charges. Partner Network is local by default; a live partner may have its own billing. Each [capstone guide](../capstones/README.md) states cleanup and limitations.
