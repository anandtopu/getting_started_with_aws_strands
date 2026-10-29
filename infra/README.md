# Optional Tier 2 AWS labs

**AWS required; core lessons remain local.** These apps create resources only when
you explicitly run CDK deployment. They have not been deployed during course
authoring. Complete [SSO, budget and region setup](../docs/AWS_SETUP.md) first.
Use a dedicated learning account and a deployment role approved for the displayed
CloudFormation changes. The application roles are narrower than that deployment role.

## Prepare and synthesize

Install Node.js 22 or newer separately. From the repository root:

```text
uv sync --group aws
npm ci --prefix infra
uv run --group aws python scripts/synth_all.py
```

The pinned CDK CLI and Python library have different version numbers. The check
uses a fictional account, disables context lookups and produces templates without
bootstrapping or deploying. The apps read `AWS_REGION` from course configuration;
keep the chosen SSO profile's region consistent with it. Review the generated
`infra/<lab>/cdk.out/*.template.json` before deployment.

| App / stack | Creates | Runtime access | Cleanup |
|---|---|---|---|
| [Knowledge Base](07_knowledge_base/app.py) / `NimbusKnowledgeLab` | S3 policy bucket, S3 vector bucket/index, Bedrock Knowledge Base and data source, service role/policy | Selected embedding model, policy prefix, one vector index | Empty the source bucket, then delete the stack |
| [Sessions](09_sessions/app.py) / `NimbusSessionLab` | Private encrypted S3 bucket with 90-day lifecycle; scoped managed policy | Read/write/list/delete only `CUS-001/` | Delete demo sessions, empty bucket, delete stack |
| [Memory](09_memory/app.py) / `NimbusMemoryLab` | AgentCore Memory with a user-preference strategy and recall-only managed policy | Read records from this memory; no event writes or deletion | Delete the entire isolated demo memory through stack deletion |

Resources that support tags carry `project=getting-started-with-aws-strands`.
Untagged children are tracked by their tagged CloudFormation stack. Policies use
explicit actions with explanatory comments in [the constructs](../common/infra_stacks.py).
Resource wildcards cover only a named bucket prefix or the account's Bedrock
knowledge-base trust boundary; there are no wildcard IAM actions.

## Optional deployment commands

First inspect the app and template. Substitute your configured profile if its
name differs from `nimbus-course`. CDK bootstrap is an account-level prerequisite;
ask the account administrator to supply it if missing. These apps have no Docker
or file assets, but an existing modern CDK bootstrap may still be required for
deployment. Bootstrap roles/buckets are separate from these lab stacks.

```text
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk deploy NimbusKnowledgeLab --app "python infra/07_knowledge_base/app.py" --profile nimbus-course
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk deploy NimbusSessionLab --app "python infra/09_sessions/app.py" --profile nimbus-course
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk deploy NimbusMemoryLab --app "python infra/09_memory/app.py" --profile nimbus-course
```

Deploy only the lab you intend to use. Copy the displayed output IDs into
`NIMBUS_KNOWLEDGE_BASE_ID`, `NIMBUS_SESSION_BUCKET`, or `AGENTCORE_MEMORY_ID` in
`.env`. These IDs are configuration, not credentials. The `SessionPolicyArn` or
`MemoryRecallPolicyArn` output can be attached to the demo role by an authorized
administrator. The latter permits recall from the one lab memory; the application
adds the customer namespace constraint. Real multi-user
systems need authenticated user-specific roles/prefix enforcement; changing a
string in a prompt is not authentication.

For the Knowledge Base, upload only the committed synthetic Markdown policies
and their `topic` metadata sidecars:

```text
uv run python scripts/tier2_lab.py NimbusKnowledgeLab inspect
uv run python scripts/tier2_lab.py NimbusKnowledgeLab ingest --execute --confirm-stack NimbusKnowledgeLab
```

The ingestion command prints its job ID. Wait until the Bedrock console reports
`COMPLETE`; a started job is not a ready index. A failed ingestion must be fixed
before querying. The module 07 example queries only `topic=refund`. The bucket,
index, embeddings and Knowledge Base must all be in a supported common region.
The embedding dimension is 256 throughout; changing the model/dimension requires
a compatible new index.

The AgentCore example uses a read-only `MemoryStore` with the stable Strands
`MemoryManager`. It reads existing preferences and does not persist the conversation.
Its offline Stubber response supplies an aisle preference.
A freshly deployed memory has no extracted preference yet; a live answer should
say it has none. Writing events and operating full managed extraction are optional
later production lessons. Do not interpret the scripted preference as an AWS result.

## Dated cost assumptions: October 29, 2026

These estimates exclude chat inference, tax and repeated experiments. They are
not a bill guarantee or a spending cap. Local Chroma, file sessions and explicit
SQLite preferences have no AWS charge.

| Resource/workload | Planning cost |
|---|---|
| S3 policy/session objects, 1 MB for one month | At a planning $0.023/GB-month, about $0.000023 storage; requests extra |
| S3 Vectors, 100 vectors × roughly 2 KB, 1,000 queries/month | About $0.000012/month storage at $0.06/GB-month, plus approximately $0.0025 query-request cost; upload, processed bytes and returned bytes extra |
| Bedrock KB | Vector store, embeddings and generation billed separately; this lab does not use paid parsing or generation in Retrieve |
| Titan embedding ingestion, 20,000 input tokens | About $0.0004 at a planning $0.02/million; verify region/model rate before use |
| S3 sessions | Storage and GET/PUT/LIST/DELETE pricing; no always-running compute |
| AgentCore short-term memory, 100 events of 3 KB | About $0.0012 ingestion at the 12 KB/event billing minimum, $0.00024 for one retrieval of each; actual-byte storage is extra |
| AgentCore 100 built-in long-term records/month and 100 retrievals | $0.075 storage + $0.05 retrieval, subject to the selected strategy and current pricing |

S3 Vectors is the selected inexpensive managed store for this tiny, infrequent
workload. It has no provisioned compute floor. We do **not** claim it is globally
the cheapest supported store: OpenSearch Serverless NextGen now scales to zero,
so older comparisons assuming a permanent OCU minimum are outdated. For comparison,
an illustrative 2.5 OCU-hours/month at $0.24/hour would be $0.60 before storage;
actual NextGen compute depends on utilization and idle periods. An existing shared
database can change the comparison. Measure your workload before choosing a store
for production.

Sources: [S3 pricing](https://aws.amazon.com/s3/pricing/),
[S3 Vectors worked example](https://aws.amazon.com/blogs/storage/optimize-agent-tool-selection-using-s3-vectors-and-bedrock-knowledge-bases/),
[OpenSearch pricing](https://aws.amazon.com/opensearch-service/pricing/),
[Bedrock pricing](https://aws.amazon.com/bedrock/pricing/),
[AgentCore pricing](https://aws.amazon.com/bedrock/agentcore/pricing/).
AgentCore short-term pricing changed in October 2026; the old $0.25/1,000-events
formula must not be used for this course date.

## Tear down and verify

The cleanup helper first shows the tagged stack's resources. It changes nothing
without both mutation flags. **The destroy action deletes all objects in that
lab's source/session bucket and all data in that lab's memory/vector resources.**
Only use isolated synthetic-data labs. It rejects unrelated stack names, missing
project tags and unexpectedly versioned buckets.

```text
uv run python scripts/tier2_lab.py NimbusKnowledgeLab destroy
uv run python scripts/tier2_lab.py NimbusKnowledgeLab destroy --execute --confirm-stack NimbusKnowledgeLab
uv run python scripts/tier2_lab.py NimbusSessionLab destroy --execute --confirm-stack NimbusSessionLab
uv run python scripts/tier2_lab.py NimbusMemoryLab destroy --execute --confirm-stack NimbusMemoryLab
uv run python scripts/find_leftovers.py
```

Run only the destroy commands for stacks you created. Confirm CloudFormation
deletion completed, then inspect leftover inventory in every used region. A scan
with access-denied errors is incomplete. Remove any separately provisioned bootstrap
resources only with the account owner's approval; they may serve other projects.

The 90-day AgentCore event expiry does not imply deletion of long-term records.
The local lesson deletes its own registered sessions/preferences; cloud user
erasure additionally needs record/event discovery, all namespace copies, snapshots
and backup policy. This isolated lab uses entire-resource deletion for complete
cloud cleanup rather than claiming that expiry is complete erasure.
