# Production resource costs and cleanup

Checked October 29, 2026. USD before tax, `us-east-1` assumptions; no free-tier credits
are subtracted. These are planning calculations, not measured bills. All `--mock` lessons
cost $0 and create no AWS resources. Local Ollama has no API fee; your machine still uses energy.

| Hosting resource | Planning rate / example | Lifetime and cleanup |
|---|---|---|
| Lambda, 1 GB x86 | About $0.0000166667 per GB-second plus $0.20/million requests; 100 × 10-second calls about $0.0167 before model/logs | Delete `NimbusLambda`; no provisioned concurrency |
| Fargate, Linux x86, 0.25 vCPU + 0.5 GB | `(0.25 × 0.000011244 + 0.5 × 0.000001235) × 3600` ≈ $0.01234/hour | Continues idle; delete `NimbusFargate` |
| ALB | $0.0225/hour plus $0.008/LCU-hour | Continues idle; delete with Fargate stack |
| Public IPv4 | $0.005/address-hour; plan at least three addresses for the two-zone ALB and one task | About $0.015/hour at three addresses; more during rollout/scale |
| Fargate deployment subtotal | About $0.04984/hour, or $36.38 per 730-hour month before LCU, secret, logs, image storage, model and traffic | A one-hour lab is inexpensive; leaving it running is not free |
| Runtime microVM | v1 $0.0895/vCPU-hour + $0.00945/GB-hour; v2 consumption $0.1276 + $0.0169 respectively | Check the actual runtime platform; memory remains billed during idle session time |
| ECR images/CDK asset S3 | ECR planning $0.10/GB-month; S3 Standard planning $0.023/GB-month plus requests | Shared bootstrap assets outlive application stack deletion |
| Secrets Manager | Planning $0.40/secret-month plus API requests | One generated Fargate bearer; destroy the isolated lab secret with stack |
| SSM standard parameter | Standard storage has no additional charge; higher-throughput API settings can cost extra | One service-name parameter, removed with stack |
| VPC, subnets, routes, security groups, roles, Cognito public app client, workload identity, Policy engine | No standalone hourly allocation charge in this design; associated usage still bills | No NAT gateway, private CA, customer KMS key or persistent EC2 instance is created |

Sources: [Lambda](https://aws.amazon.com/lambda/pricing/), [Fargate](https://aws.amazon.com/fargate/pricing/),
[ALB](https://aws.amazon.com/elasticloadbalancing/pricing/), [IPv4/VPC](https://aws.amazon.com/vpc/pricing/),
[ECR](https://aws.amazon.com/ecr/pricing/), [S3](https://aws.amazon.com/s3/pricing/),
[Secrets Manager](https://aws.amazon.com/secrets-manager/pricing/), [SSM](https://aws.amazon.com/systems-manager/pricing/).
The TLS certificate must already exist; verify the price of its chosen certificate type and DNS hosting.

| AgentCore capability | Current rate / small workload |
|---|---|
| Memory short term | $1/GB ingested, $0.20/GB retrieved, $0.10/GB-month stored; minimum billable operation sizes apply |
| Memory long term | Built-in storage $0.75/1,000 records/month; retrieval $0.50/1,000 |
| Gateway | $0.005/1,000 normal calls; search $0.025/1,000; index $0.02/100 tools/month |
| Identity | $0.010/1,000 standalone credential requests; no additional Identity charge through Runtime/Gateway |
| Code Interpreter / Browser | $0.0895/vCPU-hour + $0.00945/GB-hour; session minimums apply |
| Policy | $0.000025/authorization request; no natural-language policy generation in this course |
| Built-in evaluation | $0.0024/1,000 input tokens + $0.012/1,000 output tokens |
| Observability | CloudWatch logs, metrics, traces and queries billed separately |

[AgentCore pricing](https://aws.amazon.com/bedrock/agentcore/pricing/). The old $0.25/1,000
short-term events rate ended October 5, 2026. Built-in strategies may create several records
from one event. A 60-second tool session at an assumed 1 active vCPU and 1 GB throughout
would be about $0.00165, not a guaranteed service allocation or invoice.

CloudWatch planning examples are $0.50/GB log ingestion, $0.03/GB-month retained logs,
$0.30/custom metric-month and $0.10/standard alarm-month; traces, Insights queries and
Transaction Search add separate metering. The course metrics use two metric names and
one alarm, so continuing to publish them can cost about $0.70/month before logs/queries.
Seven-day retention bounds age, not ingestion volume. [CloudWatch pricing](https://aws.amazon.com/cloudwatch/pricing/).

The services stack adds a small encrypted S3 bucket, two Lambda functions (booking and judge),
Cognito sign-in and an initially disabled daily schedule. S3 expires the reviewed export after
one day. EventBridge Scheduler is usage-billed; beyond its applicable free tier, plan
$1/million invocations. Cognito charges depend on active users, feature tier and authentication
method; use a dedicated learning user and review the regional rate. No paid custom domain
or third-party OAuth application is created. [Scheduler](https://aws.amazon.com/eventbridge/pricing/),
[Cognito](https://aws.amazon.com/cognito/pricing/).

Model inference is additional on every host. Configure dated per-million rates in `.env` if
you want `estimate_cost` to print dollars. Scripted usage is not billed usage. Budget for
input history, tool rounds, retries and judges, not just the final answer's tokens.

Follow the exact [deployment and teardown sequence](../infra/PRODUCTION.md). A budget alert
is a notification, not a hard spending cap. Stop sessions and disable schedules first;
delete exports, application stacks and unneeded isolated assets; inspect all deployed regions.
