# Verification notes

Checked October 29, 2026. This is a Phase 1 research baseline, not an execution report. Release metadata, selected package source, official documentation, and upstream test fixtures were inspected. No model calls, account probes, deployments, installed-package tests, or full dependency resolution have been performed.

## Evidence and source precedence

The [package metadata snapshot](verification/package_metadata.json) records direct-package versions, Python requirements, extras, dependency constraints, release timestamps, and public source URLs. [Compatibility metadata](verification/compatibility_metadata.json) records candidate older versions allowed by upstream caps. The final install must use a resolver-generated lockfile; compatible-looking version numbers alone do not establish a working environment.

The SDK repository now lives at `strands-agents/harness-sdk`, with Python sources under `strands-py/`. The requested distribution remains `strands-agents` and its current stable 1.x release is 1.62.0. The newer assembled harness is a distinct project; it will not silently replace the requested SDK. See the [Python release](https://github.com/strands-agents/harness-sdk/releases/tag/python/v1.62.0), [tools release](https://github.com/strands-agents/tools/releases/tag/v0.8.10), and [Evals release](https://github.com/strands-agents/evals/releases/tag/v1.7.0).

When a current documentation page and the pinned package differ, the installed source and behavior tests govern the implementation. The relevant doc discrepancy is recorded here. Each later phase verifies every symbol and parameter it introduces before writing its examples.

## Verified version table

The table below is generated from public PyPI metadata. “Planned range” is a proposed direct constraint for Phase 2, not a claim that the complete environment has resolved. Transitive packages will be recorded in `uv.lock` after resolution. Optional packages are not all installed by the beginner quick start.

| Package | Latest observed | Planned version range | Python metadata | Install location | Source |
|---|---:|---|---|---|---|
| `strands-agents` | 1.62.0 | `>=1.62.0,<1.63.0` | `>=3.10` | foundations; provider/feature extras | [PyPI](https://pypi.org/project/strands-agents/1.62.0/) |
| `strands-agents-tools` | 0.8.10 | `>=0.8.10,<0.9.0` | `>=3.10` | foundations | [PyPI](https://pypi.org/project/strands-agents-tools/0.8.10/) |
| `strands-agents-evals` | 1.7.0 | `>=1.7.0,<1.8.0` | `>=3.10` | evals | [PyPI](https://pypi.org/project/strands-agents-evals/1.7.0/) |
| `strands-agents-builder` | 0.1.10 | `Not installed` | `>=3.10` | Excluded: archived | [PyPI](https://pypi.org/project/strands-agents-builder/0.1.10/) |
| `bedrock-agentcore` | 1.25.1 | `>=1.25.1,<1.26.0` | `>=3.10` | aws (direct SDK) | [PyPI](https://pypi.org/project/bedrock-agentcore/1.25.1/) |
| `bedrock-agentcore-starter-toolkit` | 0.3.14 | `>=0.3.14,<0.4.0` | `>=3.10` | aws deployment | [PyPI](https://pypi.org/project/bedrock-agentcore-starter-toolkit/0.3.14/) |
| `aws-cdk-lib` | 2.275.0 | `>=2.275.0,<2.276.0` | `>=3.10` | aws infrastructure | [PyPI](https://pypi.org/project/aws-cdk-lib/2.275.0/) |
| `boto3` | 1.43.121 | `>=1.43.121,<1.44.0` | `>=3.10` | foundations/AWS | [PyPI](https://pypi.org/project/boto3/1.43.121/) |
| `moto` | 5.2.5 | `>=5.2.5,<5.3.0` | `>=3.10` | dev, S3/DynamoDB | [PyPI](https://pypi.org/project/moto/5.2.5/) |
| `chromadb` | 1.5.9 | `>=1.5.9,<1.6.0` | `>=3.9` | rag | [PyPI](https://pypi.org/project/chromadb/1.5.9/) |
| `pypdf` | 6.21.4 | `>=6.21.4,<6.22.0` | `>=3.9` | rag/data | [PyPI](https://pypi.org/project/pypdf/6.21.4/) |
| `rank-bm25` | 0.2.2 | `>=0.2.2,<0.3.0` | `Not declared` | rag | [PyPI](https://pypi.org/project/rank-bm25/0.2.2/) |
| `mcp` | 2.3.0 | `>=2.1.1,<2.2.0` | `>=3.10` | multiagent/MCP | [PyPI](https://pypi.org/project/mcp/2.1.1/) |
| `opentelemetry-sdk` | 1.45.1 | `>=1.45.1,<1.46.0` | `>=3.10` | observability | [PyPI](https://pypi.org/project/opentelemetry-sdk/1.45.1/) |
| `opentelemetry-exporter-otlp` | 1.45.1 | `>=1.45.1,<1.46.0` | `>=3.10` | observability | [PyPI](https://pypi.org/project/opentelemetry-exporter-otlp/1.45.1/) |
| `fastapi` | 0.162.0 | `>=0.162.0,<0.163.0` | `>=3.10` | apps | [PyPI](https://pypi.org/project/fastapi/0.162.0/) |
| `uvicorn` | 0.54.0 | `>=0.54.0,<0.55.0` | `>=3.10` | apps | [PyPI](https://pypi.org/project/uvicorn/0.54.0/) |
| `streamlit` | 1.66.1 | `>=1.66.1,<1.67.0` | `>=3.11` | apps | [PyPI](https://pypi.org/project/streamlit/1.66.1/) |
| `matplotlib` | 3.11.2 | `>=3.11.2,<3.12.0` | `>=3.11` | rag/apps/data | [PyPI](https://pypi.org/project/matplotlib/3.11.2/) |
| `pillow` | 13.0.0 | `>=12.3.0,<12.4.0` | `>=3.10` | data/apps | [PyPI](https://pypi.org/project/pillow/12.3.0/) |
| `pytest` | 9.2.0 | `>=9.2.0,<9.3.0` | `>=3.10` | dev | [PyPI](https://pypi.org/project/pytest/9.2.0/) |
| `pytest-asyncio` | 1.4.1 | `>=1.4.1,<1.5.0` | `>=3.10` | dev | [PyPI](https://pypi.org/project/pytest-asyncio/1.4.1/) |
| `ruff` | 0.17.3 | `>=0.17.3,<0.18.0` | `>=3.7` | dev | [PyPI](https://pypi.org/project/ruff/0.17.3/) |
| `pre-commit` | 4.7.0 | `>=4.7.0,<4.8.0` | `>=3.11` | dev | [PyPI](https://pypi.org/project/pre-commit/4.7.0/) |
| `nbstripout` | 0.9.1 | `>=0.9.1,<0.10.0` | `>=3.10` | dev | [PyPI](https://pypi.org/project/nbstripout/0.9.1/) |
| `jupyter` | 1.1.1 | `>=1.1.1,<1.2.0` | `Not declared` | notebooks | [PyPI](https://pypi.org/project/jupyter/1.1.1/) |
| `rich` | 15.0.0 | `>=15.0.0,<15.1.0` | `>=3.9.0` | foundations | [PyPI](https://pypi.org/project/rich/15.0.0/) |
| `pydantic` | 2.14.1 | `>=2.14.1,<2.15.0` | `>=3.10` | foundations | [PyPI](https://pypi.org/project/pydantic/2.14.1/) |
| `python-dotenv` | 1.2.4 | `>=1.2.4,<1.3.0` | `>=3.10` | foundations | [PyPI](https://pypi.org/project/python-dotenv/1.2.4/) |
| `uv` | 0.13.6 | `==0.13.6` | `>=3.8` | External environment tool | [PyPI](https://pypi.org/project/uv/0.13.6/) |
| `reportlab` | 5.1.0 | `>=5.1.0,<5.2.0` | `<4,>=3.9` | data | [PyPI](https://pypi.org/project/reportlab/5.1.0/) |
| `awslabs.aws-documentation-mcp-server` | 1.2.3 | `==1.2.3` | `>=3.10` | Isolated uvx | [PyPI](https://pypi.org/project/awslabs.aws-documentation-mcp-server/1.2.3/) |
| `awslabs.aws-pricing-mcp-server` | 1.1.1 | `==1.1.1` | `>=3.10` | Isolated uvx | [PyPI](https://pypi.org/project/awslabs.aws-pricing-mcp-server/1.1.1/) |
| `httpx` | 0.28.1 | `>=0.28.1,<0.29.0` | `>=3.8` | apps/integrations | [PyPI](https://pypi.org/project/httpx/0.28.1/) |
| `mem0ai` | 2.2.1 | `>=2.2.1,<2.3.0` | `<4.0,>=3.10` | optional memory | [PyPI](https://pypi.org/project/mem0ai/2.2.1/) |
| `constructs` | 10.8.1 | `>=10.8.1,<10.9.0` | `>=3.10` | aws infrastructure | [PyPI](https://pypi.org/project/constructs/10.8.1/) |
| `anthropic` | 2.3.0 | `>=0.125.0,<0.126.0` | `>=3.9` | provider extra | [PyPI](https://pypi.org/project/anthropic/0.125.0/) |
| `openai` | 3.41.0 | `>=2.54.0,<2.55.0` | `>=3.10` | provider extra | [PyPI](https://pypi.org/project/openai/2.54.0/) |
| `ollama` | 0.6.3 | `>=0.6.3,<0.7.0` | `>=3.8` | foundations provider | [PyPI](https://pypi.org/project/ollama/0.6.3/) |
| `litellm` | 1.106.6 | `>=1.106.6,<1.107.0` | `<3.15,>=3.10` | provider extra | [PyPI](https://pypi.org/project/litellm/1.106.6/) |
| `hatchling` | 1.33.0 | `>=1.33.0,<1.34.0` | `>=3.10` | build backend | [PyPI](https://pypi.org/project/hatchling/1.33.0/) |
| `pytest-socket` | 0.8.1 | `>=0.8.1,<0.9.0` | `>=3.10` | dev | [PyPI](https://pypi.org/project/pytest-socket/0.8.1/) |
| `nbclient` | 0.11.0 | `>=0.11.0,<0.12.0` | `>=3.10.0` | dev/notebooks | [PyPI](https://pypi.org/project/nbclient/0.11.0/) |
| `langgraph` | 1.2.18 | `>=1.2.18,<1.3.0` | `>=3.10` | optional partner capstone | [PyPI](https://pypi.org/project/langgraph/1.2.18/) |
| `mem0-strands` | 0.1.1 | `>=0.1.1,<0.2.0` | `>=3.10` | optional memory | [PyPI](https://pypi.org/project/mem0-strands/0.1.1/) |
| `a2a-sdk` | 1.3.0 | `>=0.3.26,<0.4.0` | `>=3.10` | multiagent/A2A | [PyPI](https://pypi.org/project/a2a-sdk/0.3.26/) |

### Non-Python tooling

- `@strands-agents/sdk` **1.22.0**, requiring Node.js **>=22**, verified through the [npm registry](https://registry.npmjs.org/@strands-agents/sdk/latest) and [TypeScript release](https://github.com/strands-agents/harness-sdk/releases/tag/typescript/v1.22.0). Bonus B2 will have its own package lock and TypeScript compiler dependency, verified when implemented.
- AWS CDK CLI **2.1146.1**, verified through the [npm registry](https://registry.npmjs.org/aws-cdk/latest). The CLI and Python CDK library use different version sequences; they must not be pinned to the same number by assumption. Synthesis verifies assembly compatibility.
- AWS CLI v2, Ollama desktop/server, Node.js, and Docker are separately installed applications. Their installers/platform prerequisites will be checked in the phase that documents installation. The Python `ollama` package is only the client, not the model server.

## Compatibility decisions discovered during research

| Conflict | Decision |
|---|---|
| Latest MCP is 2.3.0, while Strands 1.62.0 declares `mcp>=1.23.0,<2.2` | Select 2.1.1 as the candidate; do not install the latest 2.3.0 blindly. Confirm both stdio and streamable HTTP in tests. |
| Latest Pillow is 13.0.0, while tools 0.8.10 requires `>=12.1.1,<13` | Select Pillow 12.3.0. |
| Latest Anthropic client is 2.3.0, while the Strands extra requires `<1` | Select the newest eligible 0.x release, 0.125.0; test the chosen model capabilities with the adapter before advertising live support. |
| Latest OpenAI client is 3.41.0, while the Strands OpenAI/LiteLLM extras require `<3` | Select 2.54.0 for the normal provider group. Keep the experimental Live provider, which requires a newer client, outside that environment. |
| Latest A2A SDK is 1.3.0; Strands extra requires `>=0.3,<0.4` | Select A2A SDK 0.3.26; do not mix protocol client major versions. |
| Strands caps LiteLLM below 1.107.0 | Preserve that upper bound; 1.106.6 is the current eligible release. |
| Community AgentCore tool extras cap `bedrock-agentcore<1.24` | Use the current 1.25.1 SDK directly through small typed course tools for Browser/Code Interpreter. Do not enable the conflicting community extras. 1.23.1 was verified only as a fallback candidate, not selected. |
| Community `mem0-memory` extra caps mem0ai below 1 and its tool is deprecated | Use `mem0-strands` 0.1.1 with mem0ai 2.2.1 and `MemoryManager`. The historical 0.1.118 candidate is not selected. |
| AWS MCP servers may carry their own dependency ranges | Run each pinned server through isolated `uvx` environments rather than add all server packages to the course interpreter. |
| Builder package still exists but its repository is archived | Exclude it from the runtime dependency set. B3 teaches reviewed tool generation using current SDK primitives and explains the archived builder as historical context. |

These are verified direct constraints. A dependency solver can still expose additional transitive conflicts, especially in optional groups. Phase 2 resolves the selected combinations and adjusts ranges with a recorded reason before committing a lockfile.

## API verification and replacements

| Topic | Evidence and implementation decision |
|---|---|
| Default agent/model | Source `strands/agent/agent.py` and `strands/models/bedrock.py` inspected in the 1.62.0 wheel. Bedrock is the default; `DEFAULT_BEDROCK_MODEL_ID` is `global.anthropic.claude-sonnet-4-6`, with region-prefix resolution also present. Module 01 inspects effective configuration without an unconfigured billable call. Normal examples explicitly use the course model helper. |
| Structured output | `structured_output_model` exists on construction and invocation; consume `result.structured_output`. `Agent.structured_output` and its async counterpart are deprecated and excluded. See [structured output](https://strandsagents.com/docs/user-guide/sdk/agents/structured-output/) and the wheel's agent implementation. |
| Mock model | `Model` requires `get_config`, `update_config`, `stream`, and `structured_output`. Stream signature includes keyword inputs for system content, invocation state, cancellation and agent metadata. Follow the [upstream scripted fixture](https://github.com/strands-agents/harness-sdk/blob/python/v1.62.0/strands-py/tests/fixtures/mocked_model_provider.py), including text/tool stream events. Implement its stubbed methods fully; do not copy `pass` bodies. |
| Hook names | Wheel exports confirm `AgentInitializedEvent`, `BeforeInvocationEvent`, `AfterInvocationEvent`, `BeforeModelCallEvent`, `AfterModelCallEvent`, `BeforeToolCallEvent`, `AfterToolCallEvent`, `BeforeToolsEvent`, `AfterToolsEvent`, `MessageAddedEvent`, and `MessageUpdatedEvent`. Use [hook event docs](https://strandsagents.com/docs/user-guide/sdk/agents/hooks-events/) and behavior tests for mutability/order. |
| Interrupts | Individual-tool and batch hooks can interrupt; tool context also supports interruption. Resume payload IDs must match the interrupted requests. Follow [interrupt docs](https://strandsagents.com/docs/user-guide/sdk/interrupts/) exactly and test approval/rejection/timeout/replay. |
| Swarm | Wheel constructor confirms `entry_point`, `max_handoffs`, `max_iterations`, `execution_timeout`, `node_timeout`, `repetitive_handoff_detection_window`, and `repetitive_handoff_min_unique_agents`. Repetitive-handoff protection is not assumed enabled by default. See [Swarm](https://strandsagents.com/docs/user-guide/sdk/multi-agent/swarm/). |
| Graph | Wheel confirms `set_entry_point`, `set_max_node_executions`, `set_execution_timeout`, and `set_node_timeout`. Parallel branches, conditions and nested patterns follow [Graph](https://strandsagents.com/docs/user-guide/sdk/multi-agent/graph/); exact result/edge contracts are tested in Phase 6. |
| A2A | `strands.agent.a2a_agent.A2AAgent` is present. Use `client_config` for authenticated transport; `a2a_client_factory` is deprecated. The community `a2a_client` tool is also deprecated. See [A2A](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agent-to-agent/). |
| MCP | `MCPClient` and both requested transports remain documented. Teach the current managed lifecycle and explicit context-manager alternative; never retain tools after their client closes. See [MCP tools](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/) and [transports](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-transports/). |
| Prompt caching | The wheel has `CacheConfig`; `cache_prompt` and model-level `cache_tools` carry deprecation notices. Use the current cache configuration/content blocks and a model that supports those cache points. Do not reuse obsolete examples. |
| Python execution | Tools 0.8.10 deprecates `strands_tools.python_repl` and directs users to `strands.vended_tools.python_repl`. Preserve explicit human consent in the lesson; verify its execution environment on Windows. See [vended tools](https://strandsagents.com/docs/user-guide/sdk/tools/vended-tools/). |
| Mem0 | Use `from mem0_strands import Mem0MemoryStore` and `from strands.memory import MemoryManager`. The old tool's get/list/delete/history operations have no store equivalent, so user deletion uses the backend API explicitly. [Mem0 integration](https://docs.mem0.ai/integrations/strands) still mentions the deprecated tool in one section; the tools release takes precedence. |
| Workflow | `strands_tools/workflow.py` exists in tools 0.8.10. Compare it with Graph rather than claim it has been removed. Verify its invocation contract before the lesson is written. |
| AgentCore Memory | `bedrock_agentcore.memory.integrations.strands.session_manager.AgentCoreMemorySessionManager` is present in the SDK wheel. Verify retention and deletion contracts in Phase 4/7, not with an invented mock of managed memory behavior. |
| Evals CLI | Wheel entry point is `strands-evals = strands_evals.cli:main`. [CLI docs](https://strandsagents.com/docs/user-guide/evals-sdk/cli/) document `run` and nonzero evaluation-failure exit codes. Test a deliberately failing evaluation gate, not only a passing command. |
| AgentCore toolkit | Wheel entry point is `agentcore = bedrock_agentcore_starter_toolkit.cli.cli:main`. Exact deploy/invoke/destroy flags are verified in Phase 7; no obsolete command sequence is assumed. |
| Builder | The [agent-builder repository](https://github.com/strands-agents/agent-builder) was archived June 3, 2026. Keep a historical explanation, replace runtime use with current typed tools, reviewed generated code and trusted loading. |

The quoted API names above were inspected; this does not imply every future lesson's complete signature has already been validated. Streaming tool payloads, hot-reload registration, community tool argument schemas, full AgentCore control-plane operations, and infrastructure resource properties still require implementation-time checks against the frozen environment.

## Stable and experimental features

The plan has **no experimental dependencies on the core learning route**.

- **B1 voice:** use stable `strands.bidi.BidiAgent`. The old `strands.experimental.bidi` namespace is a deprecated alias in 1.62.0. The brief's blanket Experimental label for voice is therefore replaced with an accurate stable-core label. Specific experimental voice providers retain their own badge.
- **Red teaming:** Evals 1.7.0 release notes explicitly graduate it from experimental. It remains optional because of cost and complexity, but is not labelled experimental merely because older material did so.
- **B4 AgentConfig:** the inspected SDK still exposes it through `strands.experimental`; this demonstration receives an **Experimental** badge and is excluded from the main path and default imports.
- **OpenAI Live:** the 1.62.0 release calls this provider experimental, and its newer OpenAI client requirement conflicts with the normal provider group. It is not planned as a runnable core example. A future opt-in addition would require an isolated environment and renewed verification.
- Experimental checkpoint/steering/context-manager APIs are not required for the course. Stable session managers, hooks, interrupts, limits, and conversation managers cover the core requirements.

## Model and AWS checks

| Use | Configuration candidate | Evidence / qualification |
|---|---|---|
| Bedrock default | `us.amazon.nova-2-lite-v1:0`, region `us-east-1` | The [model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-2-lite.html) lists the US profile and Active lifecycle. It is a low-cost candidate, not a claim that all accounts have access. Keep region/profile configurable. |
| Ollama text/tools | `qwen3:4b` | [Official model page](https://ollama.com/library/qwen3:4b) advertises tool capability and a roughly 2.5 GB download. Actual RAM use exceeds download size and depends on context length. |
| Ollama vision/tools | `qwen3-vl:4b` | [Official model page](https://ollama.com/library/qwen3-vl:4b) advertises vision/tools and a roughly 3.3 GB download; requires Ollama 0.12.7 or later. Use PDF extraction where native document blocks are unsupported. |
| Anthropic | `claude-haiku-5-5` | [Current model overview](https://platform.claude.com/docs/en/models/overview) lists the ID and tool/vision support. Check adapter parameter compatibility with the selected older client before finalizing the example. |
| OpenAI | `gpt-6-luna` | The [current model page](https://developers.openai.com/api/docs/models/gpt-6-luna) lists Chat Completions support. Tool calling on that endpoint requires `reasoning_effort="none"`, which the adapter sets for this default. Constructor checked with the selected client; live inference not run. `gpt-5-mini` was rejected as deprecated. |
| LiteLLM | Local Ollama route using the same chosen local model | Verify the provider-qualified model name with LiteLLM 1.106.6; do not silently fall back to a paid service. |
| Embeddings/voice | Exact IDs fixed in their implementation phases | Recheck model lifecycle, regional availability and provider capabilities immediately before adding these environment defaults. |
| Bedrock reranking | `cohere.rerank-v3-5:0` for `us-east-1` | The [region/model table](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank-supported.html) shows Amazon Rerank 1.0 is unavailable in that region. Local reranking remains the default. |

All IDs live in `.env.example`, not scattered through code. Availability is documentation-level verification until a learner explicitly runs a model probe. Current [Bedrock model access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) is often automatic with the required permissions, with provider/account prerequisites and potential activation delay. The course will not repeat the old universal instruction to submit a model-access request. Account-level denial is possible even after model activation prerequisites are met.

The [Bedrock lifecycle policy](https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle.html) distinguishes newer and older model policies. Check the individual model card rather than applying one lifecycle assumption to every model.

AgentCore Runtime, Memory, Gateway, Identity, Browser, Code Interpreter, Observability, Policy, and Evaluations appear in the [current service documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html). The [release notes](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html) record Evaluations becoming generally available in March 2026; it will not receive a stale preview badge. The [regional matrix](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-regions.html) must be checked per service. Feature availability is not inferred from Runtime availability alone.

[S3 Vectors integration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-integration.html) confirms Knowledge Base support. Its storage/request/embedding costs will be compared against alternatives for the course's small workload using [S3 pricing](https://aws.amazon.com/s3/pricing/). No universal cheapest-store claim or live price measurement has been made.

## Remaining gates before code can be called verified

1. Resolve dependency groups, generate a real `uv.lock`, install them, and run imports on supported interpreters.
2. Verify newly introduced APIs against both versioned source and official docs in each phase; add compatibility notes for every substitution.
3. Exercise offline examples through real SDK interfaces, including failure behavior; run meaningful notebook and protocol checks.
4. Verify resource properties with CDK synthesis and inspect resulting IAM. Synthesis is not deployment testing.
5. Check all model IDs and capability-specific parameters before emitting executable live examples. Record untested paid/provider cases honestly.
6. Measure per-module costs from documented token/resource assumptions and dated official prices. Do not promise a fixed bill.
7. Publish and inspect CI on Ubuntu/Windows and the macOS core check after the repository exists; local checks do not imply remote CI has passed.

No AWS resources have been created by this phase.

## Phase 2 foundation verification — October 29, 2026

### Dependency resolution and API contracts

`uv.lock` is an actual resolver output containing 307 packages across all dependency groups. All groups were installed together on Windows/Python 3.12.13; the default installation contains 110 distributions on Windows. Pydantic resolved to 2.14.2, a compatible patch newer than the 2.14.1 metadata snapshot. PyYAML 6.0.3 is an explicit development dependency for policy auditing. The local runner used uv 0.12.18; CI pins uv 0.13.6. [setup-uv v10.3.3](https://github.com/astral-sh/setup-uv/releases/tag/v10.3.3) and [checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1) are pinned by their verified commit hashes.

The shared helper was checked against the installed SDK source and actual constructors:

- Bedrock uses `boto_session` with region on the session, plus bounded botocore timeouts/retries. Passing `region_name` alongside `boto_session` is rejected by this SDK, so the helper does not do so.
- Ollama passes its timeout through `ollama_client_args`; text and tool capability remain model-dependent.
- Anthropic uses `client_args` for credentials/timeouts and does not force a temperature on adaptive-reasoning models. Live output is not treated as deterministic.
- OpenAI uses the current default model with `reasoning_effort="none"` on Chat Completions to permit tools. The default's older pinned client accepts the request parameters; no paid request was sent.
- LiteLLM's local route sets `api_base`, and `LITELLM_LOCAL_MODEL_COST_MAP=True` prevents its import-time remote price-map fetch. Optional imports remain lazy.
- The scripted provider implements the installed `Model` interface and drives the real Agent. Tests cover a tool result, failure feedback, structured-output validation/retry, async text streaming and accumulated usage. `AgentResult.__str__` includes a trailing newline, accounted for in comparisons. The deprecated `Agent.structured_output()` interface is not used.

### Observed checks

| Check | Observed result |
|---|---|
| All groups, Windows Python 3.12.13 | 30 passed, including Anthropic/OpenAI/LiteLLM constructor checks |
| Default `uv sync` then `uv run pytest`, Windows Python 3.12.13 | 27 passed; 3 optional-provider checks skipped |
| Default groups, Windows Python 3.13.13 in a separate environment | 27 passed; same 3 optional-provider checks skipped |
| Default example sweep on both interpreters | 1 delivered foundation example passed; future module examples not counted |
| `uv lock --check --offline`, `uv pip check` | Lock consistent; installed default packages compatible |
| `ruff check .`, `ruff format --check .` | Passed |
| `pre-commit run --all-files` | Lint, formatting and safety hooks passed; no delivered notebooks to strip |
| Repository IAM/configuration/notebook/link checks | Passed; no wildcard-action exceptions approved |
| AWS contracts | Budget request accepted by botocore Stubber; paginated resource inventory includes stack children and reports access denial; moto S3 round-trip and cleanup passed |
| Data integrity and regeneration | 45 hashed fixture files plus manifest; counts, foreign keys, totals, refunds, seats, citation pages and held-out split passed |
| Staged fixture verification | All 45 byte hashes still match after Git line-ending normalization |
| PDF/image visual review | All 10 PDF pages and 20 receipt PNGs reviewed; no overlap or clipped text found |
| Public Markdown link sweep | Passed after correcting the upstream license path; local links also checked |
| CDK discovery | Zero delivered apps in this phase; no synthesis success claimed |
| Offline readiness and budget planning CLIs | Ran successfully without AWS/model calls |

The test guard blocks external DNS, TCP and UDP through Python sockets while allowing loopback. Windows Python uses a local socket pair even to start its async event loop. The restricted execution host prevented that connection and initially hung the tests; runs with normal Windows loopback available passed while the external-traffic guard stayed enabled. This is a test guard, not a security boundary for arbitrary subprocesses or native code. Live tests are opt-in, credential discovery/exporters are disabled for normal tests, and Strands deprecation warnings are errors.

The generator writes UTF-8/LF text so Git normalization does not invalidate fixture hashes. Binary output is reproducible on the tested platform; cross-platform regeneration checks compare SQLite schema/rows, PNG pixels and PDF text because SQLite headers and compression libraries can differ. Committed binaries still receive exact byte-hash validation. Pricing estimates use explicit workloads and dated official sources in [COSTS.md](COSTS.md); they are not measured cloud bills.

### Limits and next gates

No real model calls, AWS resource creation, deployment or cleanup against an account were performed. Ollama model quality, live provider compatibility, SSO permissions, actual costs and cloud cleanup remain unverified. The GitHub workflow definitions target Ubuntu/Windows with Python 3.12 and 3.13, plus a macOS core check, but remote CI has not run and the repository has not been published. Dependency resolution does not prove every optional package's behavior; each later integration needs its own API and behavioral tests.

At the end of Phase 2, all modules remained future deliverables. The Phase 3 record below supersedes that delivery status; the whole-course definition of done remains open.

## Phase 3 Tier 1 verification — October 29, 2026

Modules 00–06 and the Booking Helper checkpoint are delivered. The dependency pins remain unchanged from Phase 2. The real SDK agent loop executes against scripted model events; network guards block external calls in tests, notebook replay and the script sweep. No AWS resources or hosted inference calls were made.

### API evidence and changes

- Checked `Agent` limits, `retry_strategy=None`, callback handlers, async invocation, all three conversation managers, `ToolContext`, async-generator progress, class/module tools, executors and reviewed directory reload against installed 1.62.0 source and executed examples. Direct `agent.tool` calls cross a thread boundary: the class-sharing lesson uses a serialized read-only SQLite connection, with a regression test.
- Structured output uses `structured_output_model` and `result.structured_output`. Tests cover invalid output repair, exhausted turn budgets, nested totals, inventory mismatch and held-out scoring.
- `CacheConfig(strategy="auto")` recognizes Anthropic model IDs in this pin; it does not automatically add Nova checkpoints. The Nova example uses explicit `cachePoint` blocks. [Bedrock caching](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) and [SDK caching](https://strandsagents.com/docs/user-guide/sdk/model-providers/amazon-bedrock-prompt-caching/) document provider-specific behavior. No real cache hit or savings is claimed.
- Nova low-effort reasoning is passed through `additional_request_fields` using `reasoningConfig`. High effort is excluded because it changes permitted token/temperature settings and can substantially increase output. Checked against [Nova reasoning](https://docs.aws.amazon.com/nova/latest/nova2-userguide/extended-thinking.html).
- Tools 0.8.10 deprecates more community integrations than the initial plan identified, including calculator, current_time, HTTP, shell, editor, think and journal. [The migration table](../modules/06_community_tools/MIGRATIONS.md) records all replacements. Executed lessons use the current vended factories and supported community tools; no legacy replacement is called merely to satisfy the older requested name.
- Vended shell, editor and Python tools are bound to a tiny `Sandbox` implementation with two exact operations, bounded paths and explicit consent. This is an educational backend, not general arbitrary-code isolation. HTTP access is constrained below the model to one exact Open-Meteo GET.
- `use_agent` inherits the configured parent model; vended `notebook` replaces journal. Deprecated Knowledge Base retrieve/memory wrappers are explained as migration context here, with full retrieval/memory implementations deferred to Tier 2.

### Verification limits

Mock answers check tool trajectories and application contracts; they do not establish model quality, vision accuracy, cache savings or live weather. Ollama downloads/inference, hosted provider calls, SSO and scoped role permissions remain untested here. Windows local execution is recorded below; the defined Ubuntu/Windows/macOS GitHub jobs remain unrun until publication. No CDK apps exist yet, so synthesis discovery reports zero apps rather than success.

### Observed Phase 3 checks

| Check | Observed result |
|---|---|
| Default `uv sync --frozen` then `uv run --frozen pytest`, Windows Python 3.12.13 | 142 passed; 3 optional-provider constructor tests skipped |
| Default groups, Windows Python 3.13.13 | 142 passed; same 3 optional checks skipped |
| Offline script sweep, Python 3.12 | All 47 entries passed: foundation + 37 examples + 7 use cases + checkpoint starter/solution |
| Exercise entry points and acceptance cases | All 21 starters run; all 21 reference solutions pass their cases, including allowed/denied requests |
| Actual Jupyter execution | All 7 notebooks executed top-to-bottom, with outputs saved only under ignored `.nimbus/`; committed notebooks have no outputs |
| Ruff lint and formatting | Passed across the delivered Python files and notebooks |
| `pre-commit run --all-files` | All hooks passed after notebook cell IDs were normalized; no saved outputs |
| Lock consistency / installed dependencies | 307 locked packages; 110 compatible default installed distributions |
| Local and public documentation links | 535 checked, zero failures |
| CDK discovery | Zero delivered apps; no deployment or synthesis success claimed |

The temporary notebook group was removed by the final default sync. Learners can reinstall it with `uv sync --group notebooks`. Notebook execution uses a kernel bound to the calling Python interpreter. Module tests inherit the repository-level offline fixture, so moving outside `tests/` does not bypass credential isolation or the external-network guard.

## Phase 4 Tier 2 verification — October 29, 2026

Modules 07–09, the Policy & Preferences checkpoint, and three optional AWS lab apps are delivered. The cumulative course has 55 examples, ten use cases, 30 exercise pairs and ten notebooks. Phases 5–8 remain pending. No AWS resources were deployed and no live model inference was performed.

### Version and API evidence

The existing frozen lock retains Strands 1.62.0, tools 0.8.10, Chroma 1.5.9, rank-bm25 0.2.2, mem0ai 2.2.1, mem0-strands 0.1.1, bedrock-agentcore 1.25.1 and aws-cdk-lib 2.275.0. The infrastructure npm lock pins aws-cdk CLI 2.1146.1. No experimental API or warning suppression was introduced.

- [Ollama embeddings](https://docs.ollama.com/capabilities/embeddings): live local retrieval uses `Client.embed`, `embeddinggemma`, explicit input lists and `truncate=False`. The same embedding identity is stored with the Chroma collection. Offline SHA-based lexical vectors are explicitly fixtures, not semantic embeddings.
- [Chroma collection configuration](https://docs.trychroma.com/docs/collections/configure): `PersistentClient`, explicit supplied embeddings with `embedding_function=None`, cosine configuration and metadata filters were checked against the installed client and real persisted-index tests. The embedding visualization was rendered and visually checked.
- [Titan embeddings](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-embed-text.html): `amazon.titan-embed-text-v2:0` uses `InvokeModel` with 256 dimensions in this lab. Converse does not supply this embedding operation. The response body is validated with an actual botocore Stubber contract.
- [Bedrock reranking support](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank-supported.html): the configurable default is `cohere.rerank-v3-5:0`; Amazon Rerank 1 is not assumed available in us-east-1. The example has an explicit local overlap heuristic and a separately identified AWS branch.
- [Strands memory](https://strandsagents.com/docs/user-guide/sdk/memory/overview/): `BedrockKnowledgeBaseStore` replaces the deprecated retrieve tool. Its test supplies an explicit VECTOR type, a topic filter and exact Retrieve request/response shapes. `MemoryManager` provides the current store interface; FileSessionManager and S3SessionManager provide session persistence. The latter completed a real SDK round trip against moto.
- [Mem0 Strands integration](https://docs.mem0.ai/integrations/strands): `Mem0MemoryStore` and `Mem0ServiceClient` replace `mem0_memory`. Tests execute the real adapter with an explicitly identified scoped backend double. Live OSS configuration selects Ollama and local Qdrant, discovers embedding dimensions, disables telemetry, closes the history database and vector client, and removes the disposable directory. The live OSS branch was not run. `delete_all` alone does not prove erasure of Mem0 history or backups.
- AgentCore compatibility change: the pinned package and [upstream session integration](https://raw.githubusercontent.com/aws/bedrock-agentcore-sdk-python/main/src/bedrock_agentcore/memory/integrations/strands/session_manager.py) still import deprecated bidi and multi-agent hook aliases. Instead of weakening the deprecation gate, this course uses a small read-only `MemoryStore` with the stable [RetrieveMemoryRecords API](https://docs.aws.amazon.com/bedrock-agentcore/latest/APIReference/API_RetrieveMemoryRecords.html) and Strands `MemoryManager`. It is course-owned integration code, not an AWS-provided session adapter. Exact service schemas, namespace filtering, bounded recall and error propagation are tested. It neither writes events nor activates automatic extraction.
- The CDK labs use S3 Vectors with a matching Titan dimension, private encrypted S3 sessions, and AgentCore Memory with a preference strategy. Explicit action lists, resource scopes and trust conditions are checked in synthesized templates. Resource lifecycle commands require a known stack name, matching project tag, and explicit mutation flags. Cleanup tests preserve an unrelated bucket. Live IAM propagation, service availability, ingestion and deletion remain unverified.

### Evaluation evidence and limitations

The [committed retrieval report](verification/tier2_retrieval_report.json) records source hit rate at three results: **11/11 lexical and 11/11 hybrid** on answerable questions. The unsupported visa question is excluded from that retrieval denominator and retained in answer evaluation. This is an observed tie using lexical fixture embeddings, not evidence of semantic improvement. Tests verify that changing golden labels does not change retrieved IDs.

The optional answer-evaluation command executed all 12 prediction/judge pairs. Predictions are produced without golden labels; only the separate judge receives the reference. Its offline judgments are intentionally scripted negatives and cannot establish faithfulness or correctness. The report labels them accordingly. Citation tests reject fabricated quotations and invalid provenance, and empty evidence produces abstention; exact quote matching does not by itself prove that an answer follows from the quoted text. The checkpoint preserves another user's preferences while deleting the selected user's registered active data. Copies held by a running agent, operating-system snapshots, exported reports and backups require separate retention handling.

Costs use dated workloads in the [lab guide](../infra/README.md), including October 2026 AgentCore consumption-based memory pricing and OpenSearch Serverless NextGen scale-to-zero behavior. No universal cheapest vector store or measured cloud bill is claimed. Live Ollama quality, managed extraction, cloud deployment/cleanup and remote Ubuntu/Windows/macOS CI remain untested.

### Observed Phase 4 checks

| Check | Observed result |
|---|---|
| Default frozen sync then pytest, Windows Python 3.12.13 | 199 passed; 8 explicitly optional checks skipped; no Strands deprecation warnings |
| Default groups, Windows Python 3.13.13 | 199 passed; same 8 optional skips |
| Python 3.12 with rag, memory, aws and notebooks groups | 205 passed; 2 unrelated optional-provider checks skipped; no Strands deprecation warnings |
| Offline script sweep with Tier 2 dependencies | All 70 entries passed; changed AgentCore CLI rechecked after the compatibility swap |
| Offline script sweep after default sync | 62 entries passed; 8 optional entries explicitly skipped |
| Actual Jupyter execution | All ten notebooks passed; changed memory notebook rerun successfully; committed outputs remain cleared |
| Exercise entry points and acceptance cases | All 30 starters run; all 30 reference solutions pass their acceptance cases |
| Optional full answer-evaluation command | All 12 prediction/judge records produced in offline mode; no live quality conclusion |
| Actual CDK CLI synthesis | All three apps synthesized after the final memory policy change; no lookups, bootstrap or deployment |
| Ruff lint and formatting | Passed for delivered Python and notebooks |
| `pre-commit run --all-files` | All hooks passed, including cleared notebooks and IAM/sample configuration checks |
| Documentation links | 688 local/public links checked with zero failures |

Default sync restores the small 110-distribution environment. Optional-group skips are reported explicitly and do not count as successes. The optional CI job installs all groups, synthesizes every app and uses `--require-all` for the script sweep; those remote jobs have not yet run.

## Phase 5: control, approvals, safety and MCP — October 29, 2026

Delivered modules 10–14, the Safe Support checkpoint and optional Guardrails CDK
app. This adds 23 focused examples, five use cases, 15 exercise pairs and five
cleared notebooks. Cumulative delivery is 78 examples, 15 use cases, 45 exercise
pairs, 15 notebooks, three checkpoints, four optional CDK apps and 100 finite
script manifest entries. Later tiers, bonus modules and capstones remain planned.

### Current API decisions and primary references

- [Strands hooks](https://strandsagents.com/docs/user-guide/sdk/agents/hooks-events/):
  use HookProvider/HookRegistry and current invocation/model/tool/message events.
  Trusted context is supplied through `invocation_state`; bare additional keyword
  arguments produce a deprecating warning in the pinned SDK. The warning filter
  catches both deprecated and deprecating wording. MessageUpdatedEvent uses an
  explicit replacement-event fixture; plain list edits do not emit it. No
  arbitrary persistence-order guarantee is made.
- [Strands interrupts](https://strandsagents.com/docs/user-guide/sdk/interrupts/):
  individual BeforeToolCallEvent, batch BeforeToolsEvent and ToolContext interrupts
  resume with matched identifiers. handoff_to_user remains a clarification tool.
  Financial approval is separately recorded and checked in a SQLite transaction;
  forged resume text is not authorization.
- [Strands MCP](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/)
  and the [official Python SDK](https://github.com/modelcontextprotocol/python-sdk):
  pinned MCP 2.1.1 uses MCPServer rather than the removed FastMCP import. Real stdio
  and streamable HTTP servers run locally even with a scripted model. Contexts
  own discovery and calls; agent-facing prefixes do not belong in direct server
  calls. Tool inventory pages are checked explicitly. HTTP authentication is a
  loopback demo token, not a production OAuth implementation.
- [AWS Documentation server](https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server)
  1.2.3 and [AWS Pricing server](https://awslabs.github.io/mcp/servers/aws-pricing-mcp-server)
  1.1.1 have exact uvx pins in the module configuration. Live server launches and
  AWS pricing responses are untested. The cost agent uses a bounded get_pricing
  wrapper; offline rates are illustrative and never called current live prices.
- [Strands Guardrails](https://strandsagents.com/docs/user-guide/sdk/safety-security/guardrails/)
  and [CloudFormation Guardrail](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-bedrock-guardrail.html):
  model attachment sets ID/version, synchronous stream processing and enabled
  trace. Explicit ApplyGuardrail grounding supplies source/query/answer tags.
  CDK's nested dictionary property names use camelCase. Configuration includes
  content, denied-topic, PII anonymization and grounding/relevance filters, plus
  a published version and ARN-scoped apply policy. No deployment occurred.

### Safety and integration evidence

Tests force a harmless export-marker proposal with the actual poisoned document
in model input; the baseline executes the marker and the policy denies it.
This is an application-boundary regression, not a claim that a live model always
ignores injection. Approval tests cover rejection, exact expiry, cross-customer
access, forged resume, changed remaining balance and concurrent replay.
Real MCP tests cover authenticated/unauthenticated HTTP, filtered capabilities,
actual booking calls, idempotency and server shutdown. FastAPI tests cover role
tokens, approve/reject routes and replay; stream tests close iterators on timeout,
disconnect and cancellation. Streamlit's actual widget runtime verifies repeated
messages, isolated sessions and clearing history.

Windows checks exposed and corrected two lifecycle bugs: Streamlit must own its
entry-point lifecycle rather than receive SystemExit from the CLI wrapper, and
the HTTP MCP server must stop its real child process before its SQLite file is
removed. Connections close explicitly; authenticated graceful shutdown has a
bounded owned-process-tree fallback. Jupyter subprocess logging uses the original
stderr file handle. A bounded queue keeps the Streamlit async stream in one
task/context. The example runner preserves Unicode failure diagnostics even on
narrower Windows terminal encodings. Twelve consecutive HTTP cleanup runs passed
after the fix, and process inspection found no remaining test servers.

Mock providers, Stubber and template synthesis verify integration contracts;
they do not establish live classifier accuracy, regional availability, IAM
permissions, model quality or cloud deletion. Local web approval pauses live in
memory; the ledger persists but restart recovery/multi-worker coordination are
outside this teaching app. Remote CI, live Ollama/Bedrock calls, AWS MCP servers,
cloud deployment and cloud teardown remain untested.

### Observed Phase 5 checks

| Check | Observed result |
|---|---|
| Windows Python 3.12.13, apps/aws/notebooks/rag/memory groups | 296 passed; 2 optional provider checks skipped; no Strands deprecation warnings |
| Default frozen installation, Python 3.12.13 | 287 passed; 11 explicitly optional checks skipped |
| Default installation, Python 3.13.13 | 287 passed; the same 11 optional checks skipped |
| Offline finite scripts with lesson dependencies | All 100 entries passed, with no dependency skips |
| Offline finite scripts with default groups | 89 entries passed; 11 optional entries explicitly skipped |
| Jupyter execution | All 15 notebooks passed; streaming notebook rechecked after final cancellation cleanup; originals remain cleared |
| Streamlit and API boundaries | Repeated messages, session isolation, Clear, authorization, approval/replay, timeout and cancellation passed |
| Actual CDK CLI synthesis | All four apps synthesized without lookups, bootstrap or deployment |
| Exercises | All 45 starters execute; all 45 reference solutions pass acceptance cases |
| Documentation links | 904 local/public references checked with zero failures |
| Frozen dependency resolution and consistency | Lock check passed; all 110 default distributions compatible |
| Ruff lint and formatting | Passed for all delivered Python files and notebooks |
| pre-commit on all files | All hooks passed, including notebook clearing and IAM/sample configuration checks |

The optional install contains 264 distributions. Skipped checks are not counted
as successes. Verification uses actual SDK loops, local protocols and Jupyter,
while paid service behavior remains explicitly unverified as described above.

## Phase 6: multi-agent systems — October 29, 2026

Modules 15–18 add 17 examples, four use cases, 12 exercise pairs, four notebooks
and Trip Planning Crew. Cumulative delivery is 95 examples, 19 use cases,
57 exercise pairs, 19 cleared notebooks, four checkpoints and 123 finite script
entries. The four optional CDK apps from earlier tiers remain unchanged.

### Checked API contracts and implementation decisions

The locked versions remain Strands 1.62.0, strands-agents-tools 0.8.10,
a2a-sdk 0.3.26 and LangGraph 1.2.18. The installed source was checked alongside
the official [agents-as-tools guide](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agents-as-tools/),
[Swarm guide](https://strandsagents.com/docs/user-guide/sdk/multi-agent/swarm/),
[Graph guide](https://strandsagents.com/docs/user-guide/sdk/multi-agent/graph/),
[A2A guide](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agent-to-agent/),
and [LangGraph graph API](https://docs.langchain.com/oss/python/langgraph/graph-api).

- Explicit async tool wrappers construct specialists through the shared model
  factory. They pass only public task evidence, validate role/reference/cents
  against catalogs, allow one attempt per role, and cap calls and elapsed time.
  A concurrent duplicate-call test confirms only three specialist models run.
- The delegated fixture uses 600 tokens versus 240 for a single agent with a
  catalog tool. This verifies accounting, not a quality improvement. Answer
  reference/topic checks and a manual factuality/usefulness rubric make that
  distinction visible.
- `Swarm` adds `handoff_to_agent`; its fixture must include the subsequent final
  assistant response before moving nodes. Both handoff/iteration ceilings use
  history length in this version. Repetition detection ends a two-agent loop
  after four visits. `execution_timeout` is checked between nodes, so an outer
  `asyncio.timeout` is used to enforce a strict whole-call deadline in the probe.
  Tests verify cooperative async-tool cleanup after both node and host timeouts.
- Revisited agents expose an SDK accounting caveat: eight fixture model calls
  use 960 tokens but the Swarm aggregate reports 1440 because cumulative usage
  can be added again. Reports retain the raw aggregate and suppress dollar
  estimates for repeated node IDs. Independent per-call telemetry is required
  for reliable billing. Ordinary distinct-node and nested totals are tested.
- `GraphBuilder` runs Agent and `MultiAgentBase` executors. Real tests cover
  concurrent flight/hotel intervals, single fan-in, conditional budget routes,
  bounded self-loops, nested graphs/swarms and propagated specialist usage.
  Exact quote approval is host-owned, fingerprint-bound, single-decision and
  expires after five minutes. Forged interrupt text, expiry or rejection yields
  no email draft. The review is local/in-memory and not a production identity
  or durable approval service. Nothing is booked or sent.
- `workflow` still exists in the tools package. The lesson creates, inspects
  and deletes actual workflow metadata in a temporary directory; it does not
  start background workers or route their models outside the course factory.
  Its pinned private manager cleanup is isolated in a compatibility helper.
  Pause/resume are unimplemented in the tool source and are not taught as working.
- The deprecated shared-agent `A2AServer(agent=...)` is replaced with
  `agent_factory(context_id)`. Each context gets an independent Agent; the
  integration test exceeds one fixture agent's request allowance across four
  contexts to catch shared-agent regressions. The server caps contexts at 16.
- The compatible A2A integration advertises **protocol 0.3.0**, not the latest
  protocol version. Compliant streaming is enabled explicitly; the Strands
  client consumes actual task/artifact events and validates the final quote.
  A generated bearer protects discovery, RPC and shutdown. Credentials stay
  in HTTP configuration; redirects and environment proxies are disabled, and
  the card's origin must match the approved endpoint. These are loopback demos
  with a single principal, not internet-ready identity/authorization systems.
- Interoperability uses an actual LangGraph `StateGraph` behind the A2A SDK's
  executor/task-store adapter in a separate process. The same Strands client
  calls both backends. Unknown remote model usage is explicitly reported as
  unavailable rather than zero. The deterministic LangGraph quote node uses
  no model. Its small cancellation handler reports a status and does not
  implement durable cancellation/recovery for production tasks.

### Verification scope

Offline checks execute real SDK loops, local subprocess transports and Jupyter
kernels. The lesson-dependency test run passed 373 tests with two optional
provider checks skipped; after adding duplicate-call/context-isolation checks,
the focused boundary suite passed all 20 tests. All 123 finite scripts and all
19 notebooks passed. The actual CDK CLI synthesized all four existing apps with
no lookups or deployment. Original notebooks remain cleared.

Windows Python 3.12.13 and 3.13.13 with default groups each passed 363 tests and
explicitly skipped 13 optional-dependency checks. No Strands deprecation warnings occurred
in the tests. Live model quality, Ollama performance, public A2A interoperability,
HTTPS/identity deployment, remote CI and all cloud deployment/teardown remain
unverified. The default paths create no AWS resources.

Frozen dependency resolution and consistency checks passed with 110 default
distributions. Ruff lint/format checks passed across 438 source/notebook files.
The documentation checker verified 1,032 local/public links with zero failures.
All 107 default-install script entries passed; 16 entries explicitly skipped
missing optional dependencies. All pre-commit hooks passed on every file,
including notebook clearing, IAM actions and sample credential checks.

## Phase 7: production, observability and AgentCore (2026-10-29)

Modules 19–21 add 22 examples, three use cases, nine exercise/solution pairs,
three notebooks and the Production Readiness checkpoint. The delivered course
now has 117 examples, 22 use cases, 66 exercise pairs, 22 notebooks and five
checkpoints. Bonus modules and capstones remain Phase 8 work.

### Versions and API checks

[The dated PyPI inventory](verification/phase7_packages.json) records installed
versions and current releases. The implementation uses Strands 1.62.0, tools
0.8.10, Evals 1.7.0, AgentCore SDK 1.25.1, toolkit 0.3.14 and CDK 2.275.0.
The tested lock retains boto3 1.43.121 and OpenTelemetry 1.45.1; newer patch
releases 1.43.122 and 1.45.2 were observed but not silently adopted. Python
3.12 and 3.13 remain the supported course versions. Authoring uses uv 0.12.18;
the previously verified CI configuration pins uv 0.13.6.

- [Strands Evals](https://strandsagents.com/docs/user-guide/evals-sdk/) supplies
  actual `Case`, `Experiment`, output and trajectory evaluators. CLI checks run
  the installed command implementation in a child process and verify exit codes.
  The twelve-case baseline passes; the deliberately incorrect response fails.
  Mock judge ratings establish the interface, not real model quality.
- MCP 2.1.1 provides `MCPServer`; the older `FastMCP` spelling is not used.
  Local Gateway lessons execute real stdio discovery and calls, with keyword
  search explicitly distinguished from AWS semantic search.
- The pinned Code Interpreter service model accepts `executeCode`. An SDK
  docstring mentioning `execute` is not treated as the API contract. Managed
  Browser uses signed CDP and fixed synthetic HTML; mocks check its lifecycle
  without claiming a browser engine executed.
- CDK's generated OnlineEvaluationConfig signature exposes `resultDestination`,
  but its CloudFormation schema rejects that property. The template supplies a
  dedicated output log group and leaves that unsupported option unset.
- Built-in evaluator ARNs have empty region and account segments, as documented
  in [AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html).
  The scheduled role grants only `Builtin.Helpfulness`. Template tests check that
  permission and the exact `amount_cents` property shared by Gateway and Cedar.
- [On-demand evaluation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/getting-started-on-demand.html)
  returns normalized scores (for example, 0.83 for Very Helpful). The scheduled
  gate rejects absent, partial, nonnumeric, nonfinite and out-of-range results,
  and scores below 0.8. This is separate from the local Evals regression gate.
- [AWS's OTLP endpoint](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-OTLPEndpoint.html)
  accepts signed protobuf over HTTP. The course projects numeric usage before
  export, tests SigV4 signing, and treats HTTP failure, malformed responses and
  rejected spans as failures. Prompts and tool content are not exported.
- Containers omit `AWS_PROFILE`: setting it to an empty string still makes
  boto3 look for an unnamed profile. Role credentials use the normal chain.
  The scheduled judge ships the locked SDK rather than relying on the version
  bundled in Lambda's base runtime. Image contexts use an explicit file allow-list.

### Verification scope and remaining live checks

All 150 finite manifest entries passed with every optional group installed and
external networking blocked. The full optional-dependency test run passed 463
tests, skipping the one explicit live-model test. The four infrastructure tests
were rerun successfully after correcting the Gateway schema and evaluator ARN.
The only Python deprecation warning came from AgentCore's runtime timestamp
implementation (`datetime.utcnow`), not Strands. It is recorded, not suppressed.

Local tests exercise actual Strands loops, HTTP adapters, MCP subprocesses,
structured Evals results, failure exit codes, JWT signatures and public policy
retrieval. AWS Stubber tests validate request shapes and cleanup, not cloud
service behavior. Mock timings are not AWS performance measurements.

No AWS resources were deployed or torn down. Live model quality, hosted sign-in,
partner OAuth consent, managed Memory extraction, Cedar enforcement, remote
Browser/Code Interpreter execution, managed judge quality and cloud telemetry
delivery remain unverified. Full managed observability needs separately reviewed
instrumentation and Transaction Search configuration. The online evaluation and
daily schedule start disabled. The OpenAPI lesson validates a target request for
an existing API; it does not create an API server.

Docker is installed but its engine was unavailable. Container image builds,
ARM64 execution and the Jaeger container UI therefore remain unverified. Source
contexts, hash-locked dependencies and local hosting adapters were checked.
Remote GitHub CI and actual AWS deployment/teardown are not claimed as passing.
See [the deployment guide](../infra/PRODUCTION.md) and
[dated resource costs](PRODUCTION_COSTS.md) for the outstanding account checks.

All 22 notebooks executed successfully into the ignored output directory; the
committed originals retain no outputs. All nine CDK apps synthesized with
`--no-lookups`, without building images or deploying. The five new apps enable
CloudFormation schema validation. CDK reported only unconfigured-feature-flag
advisories. A separate 59-package deployment environment ran the copied support
core and both HTTP adapters successfully; the exported dependency hashes match
`uv.lock` exactly. This does not replace Linux container testing.

The documentation checker examined 1,185 local/public links. Five public URLs
initially timed out and all five passed a focused retry. Ruff lint and formatting
checks passed for 534 files. Frozen resolution validated 307 lockfile entries;
all 302 installed optional-environment distributions were compatible.

Windows Python 3.12.13 and 3.13.13 default installations each passed 438 tests
with 26 explicit skips (optional dependencies or live services). The default
Python 3.12 example sweep passed 124 entries and explicitly skipped 26 requiring
optional packages; no entry failed. The default environment's 110 installed
distributions passed dependency consistency checks. All pre-commit hooks passed,
including normalization of the new notebooks' cell IDs, output clearing, IAM
actions and sample credential checks. The workspace was returned to the normal
`uv sync --frozen` dependency set after optional verification.

## Phase 8 - bonus lessons, capstones and final audit (2026-10-29)

The delivered course now has 22 core modules plus four bonus modules, 130 focused
examples (including three TypeScript examples), 26 use cases, 78 exercise/solution
pairs, 26 notebooks, five tier checkpoints and five capstones. There are 173 finite
Python script entries plus four TypeScript example/use-case scripts, and ten CDK
apps. The final reference shelf includes 90 glossary terms, 22 troubleshooting
entries and five single-page PDFs with editable Markdown sources. Each PDF was
rendered with Poppler and inspected; `scripts/build_cheatsheets.py` reproduces them.

### Verified interfaces and substitutions

- Python SDK remains 1.62.0, tools 0.8.10, Evals 1.7.0 and AgentCore 1.25.1.
  TypeScript uses `@strands-agents/sdk` 1.22.0, TypeScript 7.0.2, tsx 4.23.15,
  Zod 4.6.7 and Node types 26.6.6. Both npm and uv lockfiles are committed.
- [BidiAgent](https://strandsagents.com/docs/user-guide/sdk/bidi/agent/) is stable
  in the pinned Python SDK. The current Bedrock adapter is `BedrockNovaSonicModel`.
  The older experimental import and the unverified `BidiNovaSonicModel` name are
  not used. [Nova 2.5 Sonic's model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-2-5-sonic.html)
  backs the explicit voice model setting; region availability still needs a live check.
- The live voice extra requires an AWS CRT version incompatible with the AgentCore
  toolkit's current dependency set. B1 therefore has its own locked editable project.
  Its adapter constructs with dummy credentials and external traffic disabled;
  no voice service was invoked. Root mock voice needs no optional adapter.
- The [agent-builder repository](https://github.com/strands-agents/agent-builder)
  is archived. B3 uses a current Agent structured-output proposal, exact-template
  review and explicit tool-registry replacement. A digest alone does not make code
  safe; unknown source is rejected even with a matching digest. The second actual
  Agent invocation demonstrates that the registered replacement executes.
- [Python release 1.62.0](https://github.com/strands-agents/harness-sdk/releases/tag/python/v1.62.0)
  and [TypeScript release 1.22.0](https://github.com/strands-agents/harness-sdk/releases/tag/typescript/v1.22.0)
  support the tested public cancellation, middleware and typed-tool interfaces.
  `strands_evals.redteam` is stable in installed Evals; older experimental examples
  are not copied. The three-prompt corpus and literal breach check are regression
  fixtures, not a general safety assessment. `strands.experimental.agent_config`
  remains explicitly Experimental and appears only in B4.
- CloudOps calls the confirmed read-only Documentation search and Pricing attribute
  discovery interfaces. Tool schemas were checked against the
  [official Documentation server](https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server)
  and [Pricing server source](https://github.com/awslabs/mcp/blob/main/src/aws-pricing-mcp-server/awslabs/aws_pricing_mcp_server/server.py).
  Offline runs label these as an uncontacted reference inventory.

### Integration evidence

The trip capstone executes four actual Graph nodes and streams node progress to
Streamlit. Host arithmetic and catalog checks validate the quotes. All four agents'
usage records are retained. Weather uses a fixed Open-Meteo host and an HTTP fixture
in mock mode; it is current weather, not a future trip forecast.

The document graph passes actual PNG bytes into structured extraction, validates
amounts and records anomalies. SQLite and moto-backed DynamoDB tests prove duplicate
handling. The separate held-out invoice deliberately has incorrect printed arithmetic.
Mock extraction reads public labels; no OCR quality claim is made. Its new CDK table
is on-demand, tagged, disposable and has only table-scoped PutItem/GetItem permissions.

The flagship combines the real interrupt ledger, policy retrieval, preferences,
Guardrail model configuration, Evals and local numeric OTLP export. Its fresh-process
trace run captured 136 exported spans and 136 local OTLP batches. The Runtime copilot
operation now hosts policy retrieval, JWT-bound Memory and Gateway, with a configured
Guardrail. Local ASGI and real MCP tests verify its actual handler, credential exclusion
and authentication-before-service-access. The optional Runtime IAM policy references
only the selected Memory and Guardrail and is conditional on configuration. Human
approval remains a trusted-host responsibility and mutates only synthetic local data.
No production payment service or hosted supervisor UI is implied.

The optional full suite passed 505 tests with one explicit live-service skip. After
the document-stack check and trip usage assertions were added, the ten affected
capstone checks all passed. Python 3.13's default installation passed 473 tests with
34 explicit optional/live skips. TypeScript type-checking, five tests and all four
finite scripts passed. Both uv locks and all 302 installed optional distributions
passed consistency checks. All 173 Python script entries passed in the optional
environment. Final notebook, synthesis, default Python 3.12 and publication results
are recorded in the final audit below when completed.

No live model inference, AWS deployment or cloud teardown was performed. The
upstream AgentCore runtime emitted its existing Python datetime deprecation warning;
no Strands deprecation warning was accepted. See the [definition of done](DEFINITION_OF_DONE.md)
for live-model, device, Docker, managed-service and timed-onboarding limits.

### Final local audit

All 26 notebooks executed top to bottom with outputs retained only in ignored
scratch copies. All ten CDK apps synthesized successfully without AWS lookups or
deployment. Ruff and formatting passed. The final public/local link sweep checked
1,564 links with zero failures. GitHub repository creation succeeded under the
signed-in account; the verified clone URL is now in the root README. Publication
and CI results are recorded separately from these local checks.

The final default Python 3.12.13 run also passed 473 tests with 34 optional/live
skips, matching Python 3.13.13. Its 110 installed distributions passed dependency
consistency checks. The normal beginner installation is restored after the full
optional checks. No optional-group skip is counted as a passing integration.
