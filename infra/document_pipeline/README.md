# Optional DynamoDB document storage

**AWS required.** Local SQLite is free and is the default. This app creates one
on-demand DynamoDB table and one managed IAM policy. Both belong to the tagged
`NimbusDocuments` stack. The table is disposable and uses `RemovalPolicy.DESTROY`;
stack deletion destroys its records. Never use this teaching stack for real documents.

The managed policy grants only `dynamodb:PutItem` and `dynamodb:GetItem` on this
table. Attach its output ARN to your approved application role or SSO permission
set through your account administrator; the stack does not broaden your login.
Image bytes stay local; stored records contain validated extraction and anomaly flags.

## Prepare and inspect

Complete [SSO, budget and region setup](../../docs/AWS_SETUP.md). From the root:

```text
uv sync --group aws
npm ci --prefix infra
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk synth --app "python infra/document_pipeline/app.py" --no-lookups
```

Review the table name output and narrow policy in the synthesized template.
For learners who choose a live deployment, after the account is bootstrapped:

```text
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk deploy NimbusDocuments --app "python infra/document_pipeline/app.py" --profile nimbus-course
```

Set `NIMBUS_DOCUMENT_TABLE` to the TableName output and use the same AWS region
and authorized profile. Run the [pipeline](../../capstones/03_document_intelligence/README.md)
with `--dynamodb`, without `--mock`. This also invokes the selected live image model.

## Cost estimate

There is no hourly table capacity charge in this on-demand configuration. Using
US East (N. Virginia) Standard illustrative rates checked 2026-10-29, 100 writes
of records at most 1 KB cost about $0.000063 at $0.625 per million write units.
Storage, reads, larger items and model image/token charges are additional. Rates
and free-tier eligibility vary; check [DynamoDB pricing](https://aws.amazon.com/dynamodb/pricing/)
and [Bedrock pricing](https://aws.amazon.com/bedrock/pricing/) before deployment.
IAM policy storage has no separate fee. No backups, streams or global replicas
are configured by this app. Budgets alert; they are not hard spending caps.

## Tear down

Export only synthetic records you want to keep, detach the managed policy from
any role/permission set you attached it to, then delete the stack:

```text
uv run --group aws node infra/node_modules/aws-cdk/bin/cdk destroy NimbusDocuments --app "python infra/document_pipeline/app.py" --profile nimbus-course
uv run python scripts/find_leftovers.py --regions us-east-1
```

Inspect the selected region in the leftover report. Shared bootstrap resources
are separate; do not delete an account's shared bootstrap stack as course cleanup.
