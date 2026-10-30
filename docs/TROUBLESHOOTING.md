# Troubleshooting

Start with `uv run python scripts/check_env.py`. Add `--aws` or `--ollama` only when you intentionally want service checks. Errors may include provider-specific prefixes; the fragments below are the parts to match. Never paste credentials or customer data into a bug report.

## `AccessDeniedException`

Bedrock model invocation is denied.

Check the named SSO role, model permission, region and model access requirements. Run `uv run python scripts/check_env.py --aws`. Do not grant AdministratorAccess; inspect the denied action and resource.

## `ValidationException`

A model ID, inference profile, message or model setting is invalid.

Check MODEL_ID against the current model/profile available in AWS_REGION. Some models require an inference profile. Remove unsupported temperature/reasoning combinations; inspect Module 02.

## `ThrottlingException`

The service has reached a request or token quota.

Reduce concurrency and token limits; use bounded retries with backoff. Check your account quota before requesting an increase. Retries can still incur charges.

## `Token has expired and refresh failed`

The AWS SSO session needs renewal.

Run `aws sso login --profile nimbus-course`, then verify the selected profile. Do not copy temporary credentials into .env.

## `The config profile could not be found`

AWS_PROFILE names a profile that does not exist.

Run `aws configure sso --profile nimbus-course`, or choose an existing profile. Keep profile and region settings consistent.

## `does not support tools`

The selected Ollama model cannot perform tool calls.

Use a current tool-capable model from the setup module and run its tool smoke test. A text-only success does not demonstrate tool support.

## `Connection refused`

Ollama or a local protocol server is not listening.

Start Ollama, verify OLLAMA_HOST, and confirm the model was pulled. For course protocol lessons, let the supplied process manager start and stop its server.

## `MCPClientInitializationError`

MCP transport startup failed or the client is used outside its lifecycle.

Keep tool discovery and Agent invocation inside `with client:`. Inspect the child server stderr, installed packages and executable path. Never move returned client-bound tools beyond that context.

## `asyncio.run() cannot be called from a running event loop`

Jupyter already owns an event loop.

Use `await agent.invoke_async(...)` in a notebook. The course notebooks use a bounded worker helper when mirroring complete synchronous CLI scripts.

## `ModuleNotFoundError: No module named common`

The editable course package is not installed in this interpreter.

Run `uv sync` from the repository root and execute scripts with `uv run python ...`. Select that same environment as your notebook kernel.

## `FileNotFoundError`

A path is relative to the wrong working directory.

Run documented commands from the repository root. Use pathlib and quote paths with spaces. Do not paste a Unix backslash continuation into PowerShell; commands here fit on one line.

## `Cannot find package @strands-agents/sdk`

The TypeScript dependencies are missing.

Run `npm ci --ignore-scripts --prefix modules/bonus/B2_typescript`, then `uv run python scripts/check_typescript.py`.

## `SSM parameter /cdk-bootstrap/`

The target environment has not been bootstrapped for the CDK qualifier.

Ask the learning account administrator to bootstrap the selected account/region. Synthesis does not deploy or bootstrap. Do not replace the runtime role with the bootstrap deployment role.

## `This CDK CLI is not compatible with the CDK library`

The global CDK CLI is too old.

Use `npm ci --prefix infra` and the repository-pinned CLI through `scripts/synth_all.py`. Check `node --version` is 22 or newer.

## `Cannot connect to the Docker daemon`

The Docker engine is stopped or unavailable.

Start Docker Desktop or the Docker service, then run `docker info`. Inspect the documented architecture and build context before building Runtime or Lambda containers.

## `exec format error`

A container image has the wrong CPU architecture.

Build for the architecture required by the target hosting service. Rebuild from the documented Dockerfile and review its platform option; do not reuse an incompatible local image.

## `Source is unreviewed or changed after approval`

Generated tool source differs from the exact reviewed template or digest.

Review the changed source and contract tests; only approved templates can load. Do not remove the check to make arbitrary model-generated code executable.

## `No solution found when resolving dependencies`

Voice and the AgentCore toolkit require different AWS CRT versions.

Use the isolated locked B1_voice project for live voice. Root mock voice needs no extra adapter. Do not force conflicting dependency versions.

## `ScriptedModel exhausted`

The mock received more model calls than its fixture provides.

Check the tool name, expected turns and retry path. Create a fresh fixture for a new invocation; do not silently recycle old responses.

## `ConditionalCheckFailedException`

A document fingerprint already exists in DynamoDB.

The pipeline treats this specific conditional failure as a duplicate and keeps the original record. Other service errors still propagate.

## `Support release blocked by policy evaluation`

One or more policy cases failed the release gate.

Read the saved evaluation cases and actual citations before changing prompts. Do not lower the threshold merely to pass a release.

## `Address already in use`

A local test or UI port is occupied.

Stop the previous process you started, or choose another port. Use the supplied finite protocol runners, which own their server cleanup.

## Useful guides

- [Setup](../modules/00_setup/README.md)
- [AWS identity and model access](AWS_SETUP.md)
- [Production inventory and teardown](../infra/PRODUCTION.md)
- [Verified versions and known limits](VERIFICATION_NOTES.md)
