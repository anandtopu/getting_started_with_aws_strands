# Tier 5 | Production on AWS

Modules 19-21. [Printable PDF](../output/pdf/05_production.pdf).

## Release gate

Evaluate task accuracy, grounded citations, denied actions and failure paths before deployment. A passing mock suite proves contracts, not live-model quality.

## Observability

Use traces/spans for timing and metrics for aggregate behavior. Keep prompts, credentials and PII out of exported telemetry. Set retention and inspect exports.

## Choose hosting

Local: fastest iteration. Lambda: bounded short calls. Fargate: container control with ongoing costs. AgentCore Runtime: managed agent hosting and sessions.

## AgentCore map

Runtime hosts; Memory stores events/records; Gateway exposes tools; Identity validates access; Policy enforces tool rules; Evaluations measures behavior.

## Verify locally first

uv sync --all-groups
npm ci --prefix infra
uv run --all-groups python scripts/synth_all.py

## Before deployment

Review the synthesized IAM and resources. Confirm model/profile/region, SSO, budget and deployment account. Build the correct container platform. Never deploy by smoke test.

## Teardown sequence

Stop schedules and active sessions; detach external policy attachments; delete app stacks; clean retained logs/assets as documented; inspect tagged leftovers in each used region.

## Checkpoint

Present evaluation evidence, scoped IAM, a resource/cost inventory and teardown commands. Record live AWS, Docker and onboarding checks separately from local passes.

See [the feature map](../docs/FEATURE_MAP.md) for source examples and [costs](../docs/COSTS.md) for live pricing.
