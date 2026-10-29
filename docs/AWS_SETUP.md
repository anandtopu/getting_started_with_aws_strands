# Safe AWS setup for Nimbus

The offline and Ollama routes need no AWS account. Use this guide only for the hosted route. Foundation scripts create no AWS resources automatically. The optional budget helper creates one tagged monthly budget only when you explicitly pass `--create`; it is never run by tests or setup.

## 1. Use IAM Identity Center

An identity is who you are; an IAM policy is what you may do. IAM Identity Center lets you sign in through a browser and obtain temporary credentials. Ask your account administrator to enable Identity Center, create your user, and assign a course permission set to the intended AWS account. For a personal learning account, use an existing authorized administrative identity to perform setup. Never use root for these lessons or attach AdministratorAccess to an agent.

In the AWS console, open **IAM Identity Center**, choose its home region, and enable the appropriate instance for your organization. Under **Users**, create your user and complete its invitation. Under **Permission sets**, create a custom course set with only the model access described below. Assign the user/group and permission set under **AWS accounts**. Billing/budget setup may require an administrator's separate billing permissions; those do not belong to the agent's role. An organization may already manage all these steps for you.

Use the [Identity Center setup guide](https://docs.aws.amazon.com/singlesignon/latest/userguide/get-set-up-for-idc.html) for your account's exact setup path. An organization's SSO region and your Bedrock inference region need not be the same.

## 2. Install AWS CLI v2 and configure a named profile

Install the platform-specific AWS CLI v2 package from the [official installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html). Do not install the old Python `awscli` package as a substitute for v2. Verify `aws --version` reports version 2.

```text
aws configure sso --profile nimbus-course
aws sso login --profile nimbus-course
```

The wizard asks for a session name, your access-portal start URL, the SSO region, registration scope, account and permission set. Choose the account assigned above and use `us-east-1` as the initial CLI service region if your administrator permits it. Browser authentication caches temporary SSO tokens. [AWS CLI SSO documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html) explains token refresh and profiles.

Set `AWS_PROFILE=nimbus-course` and `AWS_REGION=us-east-1` in `.env`. Never put `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, or temporary session credentials there. On deployment, workload roles will supply credentials through the normal SDK credential chain instead of a laptop SSO profile.

## 3. Create a budget before billable lesson calls

Identity setup and creating the budget are prerequisites to this rule. Before invoking models or deploying infrastructure, create a monthly **$10 actual-cost budget** with alerts at 50%, 80% and 100%, plus a forecast alert if useful. This is an account-wide budget, so it catches untagged costs too. A budget alert is not a hard spending limit; billing data and notifications can be delayed.

In **Billing and Cost Management → Budgets → Create budget**, choose a monthly cost budget, USD 10, and account-wide scope. Add your email notifications and complete any recipient verification. Confirm the budget appears in the list and the intended month/account are correct. Use [AWS's budget guide](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-create.html) when the console labels differ.

For a repeatable, tagged alternative, the repository includes [budget.py](../scripts/budget.py). Inspect its proposed request first:

```text
uv run python scripts/budget.py --email learner@example.com
```

Replace the example email with your own address before creation. The default only prints a local plan. To create it after signing in:

```text
uv run python scripts/budget.py --email learner@example.com --create
```

This creates `nimbus-course-monthly`, tagged `project=getting-started-with-aws-strands`, with actual-cost alerts at 50%, 80% and 100%. It does not configure paid Budget Actions. Monitoring budgets and email notifications are free under the [current AWS Budgets pricing](https://aws.amazon.com/aws-cost-management/aws-budgets/pricing/); paid action features are separate. Expected ongoing budget cost: $0/month for this configuration.

You normally keep the alert until all course resources are removed. Delete it explicitly with:

```text
uv run python scripts/budget.py --delete
```

Check the budget list afterward. The resource-tagging leftover scan does not cover budgets; this check is separate. Both create and delete commands are user actions; the assistant has not executed them.

## 4. Choose a region and verify model access

Use a region where both the selected model and required services are available. The initial Bedrock candidate is `us.amazon.nova-2-lite-v1:0`, a US cross-region inference profile. A profile routes requests to supported model regions; its policy needs permission for the profile and its destination foundation-model ARNs. Organizations can restrict destinations, which can prevent an otherwise valid request.

Review the [Nova 2 Lite model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-2-lite.html), [model access instructions](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html), and [AgentCore regional availability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-regions.html). Model activation is often automatic with appropriate permissions; third-party subscriptions, provider prerequisites and account-level restrictions still apply. Do not assume a historical “request access” console workflow is required for every model.

First run the offline check. After your budget exists, the second command reads identity, profile and availability metadata. It does not generate tokens:

```text
uv run python scripts/check_env.py
uv run python scripts/check_env.py --aws
```

To test actual model access, explicitly opt into one short request:

```text
uv run python scripts/check_env.py --probe --accept-cost
```

The probe requests up to 64 output tokens and has bounded retries. Even a successful metadata check does not guarantee inference permission. An expired SSO token requires another `aws sso login --profile nimbus-course`.

## Permissions and why they exist

| Capability | Actions | Scope and reason |
|---|---|---|
| Agent inference | `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream` | Exact chosen inference profile and foundation-model ARNs. Converse uses these IAM permissions; streaming needs the second action. |
| Model readiness | `bedrock:GetInferenceProfile`, `bedrock:GetFoundationModelAvailability` | Separate learner diagnostic permissions for the selected profile/model; verify service-supported resource scopes. Not needed by a running agent that only invokes. |
| Tag inventory | `tag:GetResources` | Read-only discovery; AWS requires wildcard resources for this list operation. Never wildcard actions. |
| Stack inventory | `cloudformation:DescribeStacks`, `cloudformation:ListStackResources` | Read-only stack listing and child discovery. Listing stacks requires broad resource scope; keep these permissions on the learner's inventory role. |
| Budget lifecycle | `budgets:ModifyBudget`, `budgets:ViewBudget` and tag permissions where required | Scoped budget administration by a billing-capable identity; never added to the runtime agent. Console paths can need additional read permissions. |

The [local IAM policy writer](../scripts/write_iam_policy.py) emits the agent's inference-only policy from explicit ARNs, with no AWS calls. Supply the profile ARN and every model ARN returned by `GetInferenceProfile`. It rejects wildcard ARNs. Each action has a purpose comment in the source; the generated JSON uses descriptive `Sid` values. An administrator attaches it to the intended permission set. Do not copy a broad managed policy merely to suppress an access error.

Deployment roles, S3 session policies, Guardrails, Knowledge Base and AgentCore permissions arrive with their respective later lessons and will be checked from synthesized infrastructure. No role with those permissions is created in Phase 2.

## Clean up and verify

The foundation demo and model probes create no deployed infrastructure. For later optional AWS labs, run the lesson's teardown, then:

```text
uv run python scripts/find_leftovers.py --regions us-east-1 us-west-2
```

List every region actually used. Exit code 0 means no matching resources were found within the stated scan scope; 1 means resources remain; 2 means a scan failed or was incomplete due to errors. Current coverage is the Resource Groups Tagging API and active tagged CloudFormation stacks. It does not cover all global resources, untagged retained assets, or every managed-service session. Follow the resource inventory in each later lesson as well. Never interpret a permission error as a clean account.

Sign out when finished with `aws sso logout`. Delete the budget only after cleanup is verified. Never delete a shared CDK bootstrap stack without confirming that other projects do not use it.
