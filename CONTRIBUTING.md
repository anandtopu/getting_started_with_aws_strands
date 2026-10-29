# Contributing

Help a learner complete one concrete task. A useful contribution fixes a failing command, explains a confusing concept, adds an offline regression test, or verifies a documented service contract.

## Local workflow

Use Python 3.12 or 3.13 and uv. Work from the repository root:

```text
uv sync
uv run pre-commit install
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python scripts/run_all_examples.py
uv run python scripts/check_links.py
uv run python scripts/synth_all.py
```

Installation needs network access. The default tests and example sweep block external Python socket connections, permit local loopback for Python's async runtime, and use synthetic data. Live tests require explicit `--live`; never add credentials to CI to make ordinary tests pass. The socket guard is a test aid, not an operating-system security boundary.

Use `uv sync --group providers` to test optional provider constructors, or `uv sync --all-groups` for the complete dependency selection. Keep imports for optional integrations inside the functions that use them. Update `uv.lock` with `uv lock` whenever dependencies change; explain adapter constraints in the verification notes.

## Lesson standard

Follow the module template in the implementation plan's source brief. Introduce one idea per example, keep examples around 120 lines, and supply a `main()` entry point. Explain the command, expected output, concepts, cost, and resources in the opening docstring. Mark the central line with `# KEY IDEA:`. Select models through `common.models.get_model()` except in the provider lesson itself.

Test behavior through the real Strands loop using `common.testing.ScriptedModel`. Include the failure path and repair. A scripted answer does not verify model quality. Keep held-out evaluation labels separate from agent inputs. Store mutable outputs under `.nimbus/`, never in `data/`. Strip notebook outputs before committing.

Every delivered module needs its README walkthrough, three or more examples, use case, three exercises and solutions, quiz, and meaningful tests. Add each runnable example to `scripts/examples_manifest.json`. Update the feature map only when the corresponding files exist. Planned rows remain explicitly planned until delivery.

## AWS changes

Keep deployment opt-in. Tag supported resources with `project=getting-started-with-aws-strands`, document untaggable children, and provide a resource inventory, cost assumptions and teardown command. Explain each IAM action beside the policy code. Avoid wildcard actions; any exception must have a narrow, reviewed rationale and be represented in the IAM audit. Test synthesized policies as well as handwritten policies. Synthesize without AWS lookups.

No AWS access keys belong in `.env`, source, screenshots, logs, or issue reports. Use SSO locally and scoped roles in deployed workloads. Keep tool consent enabled. Test approval rejection, timeout, repeated requests, and authorization at the tool boundary when changing sensitive tools.

## Before opening a pull request

Describe the learner's problem, changed behavior, checks run, and checks you could not run. Include relevant versions and synthetic reproduction steps. Do not say CI or a live deployment passed unless you observed it. Confirm local links work; run `scripts/check_links.py --external` separately when changing external references.

The data generator uses seed 731 and a fixed reference date. To update fixtures deliberately, run `uv run python scripts/build_data.py --overwrite`, inspect the manifest changes, review all PDF pages and receipt images, then run the integrity tests. Explain changes to policies or golden labels in the changelog.

Contributions use the [MIT license](LICENSE) and follow the [code of conduct](CODE_OF_CONDUCT.md).
