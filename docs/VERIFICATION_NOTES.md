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

Modules 00–21, notebooks, exercises/solutions, checkpoints, infrastructure, bonus modules and capstones remain future-phase deliverables. Planned feature-map paths are deliberately not links to nonexistent files. Phase 3 will implement Tier 1, modules 00–06; the later whole-course definition of done is not yet satisfied.
