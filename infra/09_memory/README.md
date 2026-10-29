# Optional AgentCore Memory lab

Read the shared [setup, resource inventory, costs, deployment and teardown guide](../README.md) before using this app. [app.py](app.py) selects the stack; [the shared stack definitions](../../common/infra_stacks.py) create its resources.

Run `uv run --group aws python scripts/synth_all.py` from the repository root after `npm ci --prefix infra`. Synthesis creates local templates only. Deployment is opt-in; live permissions and teardown have not been verified against an AWS account.
