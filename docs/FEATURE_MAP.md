# Feature map: course coverage contract

Phase 4 Tiers 1–2 edition · October 29, 2026

Modules 00–09 and the first two checkpoints are delivered. Their paths below link to existing files. Modules 10–21, bonus modules and capstones remain planned; their paths stay plain code text. The final audit will reject missing files or unimplemented coverage.

## Delivered foundation

| Capability | Implementation | Evidence |
|---|---|---|
| Bedrock, Ollama, Anthropic, OpenAI and LiteLLM selection | [Model helper](../common/models.py), [configuration](../common/config.py) | [Provider and real-loop contracts](../tests/test_models.py) |
| Scripted text, tools, validation retry, streaming and metrics | [Scripted provider](../common/testing.py), [runnable demo](../scripts/foundation_demo.py) | [Agent tests](../tests/test_models.py), [example runner](../scripts/run_all_examples.py) |
| Reproducible Nimbus data, PDF and receipts | [Generator](../scripts/build_data.py), [dataset guide](SYNTHETIC_DATA.md) | [Integrity/reproduction tests](../tests/test_data_integrity.py) |
| SSO readiness, budgets, scoped inference policy and resource inventory | [AWS setup](AWS_SETUP.md), [costs](COSTS.md) | [Offline AWS contracts](../tests/test_foundation_operations.py) |
| Credential/IAM checks, local links, clean notebooks and CI | [Repository tests](../tests/test_repository_contract.py), [CI](../.github/workflows/ci.yml) | Local verification only; remote CI not yet run |

Each feature receives plain-English teaching, a runnable example, a realistic use case, and exercises with solutions. Related features can share an example; if that exceeds roughly 120 lines, split it and update this contract. Each module also has three exercises, a notebook, quiz, and tests as specified in the [implementation plan](IMPLEMENTATION_PLAN.md).

**AWS labels:** No = can run with local inference; Optional/Yes identifies the specific cloud branch and local alternative. Offline fixture replay tests application behavior only. Models need tool calling for tool-based structured output, tools, retrieval, approvals, MCP and multi-agent work; image examples additionally need vision.

**Current API substitutions:** vended `python_repl` replaces the deprecated community version; `mem0-strands` replaces `mem0_memory`; `A2AAgent` replaces the deprecated community A2A client. Voice and red teaming use their stable paths. See [verification notes](VERIFICATION_NOTES.md).

## 00_setup: Setup and orientation

Assistant v0 · [Module guide](../modules/00_setup/README.md) · [Use case](../modules/00_setup/use_case/orientation.py) · [Tests](../modules/00_setup/tests)

| Feature coverage | Delivered example | AWS required / local alternative | Official reference |
|---|---|---|---|
| Model-driven agents versus fixed workflows; tokens; ecosystem map (Python, TypeScript, tools, Evals, builder, Bedrock, AgentCore, MCP, A2A) | [01_agent_or_workflow.py](../modules/00_setup/examples/01_agent_or_workflow.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/) |
| Python, uv, pip/venv fallback, Ollama tool-capable model and configuration checks | [02_local_readiness.py](../modules/00_setup/examples/02_local_readiness.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/) |
| Identity Center, CLI v2 SSO, budget-before-billing gate, region and model-access checks | [03_aws_readiness.py](../modules/00_setup/examples/03_aws_readiness.py) | Yes; local readiness instead | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/) |
| First configured agent call and token/latency inspection | [04_first_call_metrics.py](../modules/00_setup/examples/04_first_call_metrics.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/) |

## 01_first_agent: Your first agent

Assistant v1 · [Module guide](../modules/01_first_agent/README.md) · [Use case](../modules/01_first_agent/use_case/faq_responder.py) · [Tests](../modules/01_first_agent/tests)

| Feature coverage | Delivered example | AWS required / local alternative | Official reference |
|---|---|---|---|
| Agent defaults inspected safely; configured Agent, system_prompt and synchronous invocation | [01_hello_agent.py](../modules/01_first_agent/examples/01_hello_agent.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/) |
| AgentResult message, stop_reason, metrics, and agent.messages | [02_result_and_messages.py](../modules/01_first_agent/examples/02_result_and_messages.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/) |
| Default printing, null_callback_handler, and custom callback handler | [03_callbacks.py](../modules/01_first_agent/examples/03_callbacks.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/) |
| Async/await primer and invoke_async | [04_async_call.py](../modules/01_first_agent/examples/04_async_call.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/) |
| Agent/event loop; model decision, tool execution, continuation and stop | [05_follow_the_loop.py](../modules/01_first_agent/examples/05_follow_the_loop.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/) |

## 02_model_providers: Model providers

Assistant v1 · [Module guide](../modules/02_model_providers/README.md) · [Use case](../modules/02_model_providers/use_case/provider_comparison.py) · [Tests](../modules/02_model_providers/tests)

| Feature coverage | Delivered example | AWS required / local alternative | Official reference |
|---|---|---|---|
| BedrockModel; model ID, region, boto3 profile/session, temperature, max tokens and inference profiles | [01_bedrock_settings.py](../modules/02_model_providers/examples/01_bedrock_settings.py) | Yes; other providers instead | [Documentation](https://strandsagents.com/docs/user-guide/sdk/model-providers/) |
| Anthropic, OpenAI, Ollama and LiteLLM; overview of other supported providers | [02_provider_switch.py](../modules/02_model_providers/examples/02_provider_switch.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/model-providers/) |
| Runtime configuration changes; token usage to dated cost estimate | [03_runtime_settings_and_cost.py](../modules/02_model_providers/examples/03_runtime_settings_and_cost.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/model-providers/) |
| Build it yourself: minimal Model text stream and explicit unsupported structured output; common.testing extends it to tool events | [04_custom_model.py](../modules/02_model_providers/examples/04_custom_model.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/model-providers/) |
| CacheConfig and supported Bedrock prompt-cache settings | [05_prompt_cache.py](../modules/02_model_providers/examples/05_prompt_cache.py) | Yes; uncached local comparison | [Documentation](https://strandsagents.com/docs/user-guide/sdk/model-providers/) |
| Model-specific reasoning configuration and capability validation | [06_reasoning.py](../modules/02_model_providers/examples/06_reasoning.py) | Optional; capable local model | [Documentation](https://strandsagents.com/docs/user-guide/sdk/model-providers/) |

## 03_conversations: Conversations, messages and multimodal input

Assistant v2 · [Module guide](../modules/03_conversations/README.md) · [Use case](../modules/03_conversations/use_case/trip_chat.py) · [Tests](../modules/03_conversations/tests)

| Feature coverage | Delivered example | AWS required / local alternative | Official reference |
|---|---|---|---|
| Text content blocks, agent.messages, multi-turn state and role/constraints/tone/output prompts | [01_multi_turn.py](../modules/03_conversations/examples/01_multi_turn.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/conversation-management/) |
| SlidingWindowConversationManager, SummarizingConversationManager, NullConversationManager and overflow | [02_conversation_windows.py](../modules/03_conversations/examples/02_conversation_windows.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/conversation-management/) |
| Image content blocks and vision capability checks on a synthetic receipt | [03_receipt_image.py](../modules/03_conversations/examples/03_receipt_image.py) | No; vision model needed | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/conversation-management/) |
| Document blocks on supported models; local PDF text extraction with page provenance | [04_policy_document.py](../modules/03_conversations/examples/04_policy_document.py) | Optional; local extraction | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/conversation-management/) |

## 04_structured_output: Structured output

Assistant v3 · [Module guide](../modules/04_structured_output/README.md) · [Use case](../modules/04_structured_output/use_case/ticket_triage.py) · [Tests](../modules/04_structured_output/tests)

| Feature coverage | Delivered example | AWS required / local alternative | Official reference |
|---|---|---|---|
| Pydantic primer; structured_output_model on Agent/call and result.structured_output | [01_typed_ticket.py](../modules/04_structured_output/examples/01_typed_ticket.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/structured-output/) |
| Nested schemas, enums and optional fields; extract a confirmation email | [02_nested_itinerary.py](../modules/04_structured_output/examples/02_nested_itinerary.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/structured-output/) |
| Validation failure, correction, retry limits and malformed output tests | [03_validation_retry.py](../modules/04_structured_output/examples/03_validation_retry.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/structured-output/) |
| Structured answers after tool use; labelled ticket accuracy and CSV export | [04_structure_with_tools.py](../modules/04_structured_output/examples/04_structure_with_tools.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/structured-output/) |

## 05_building_tools: Building tools

Assistant v4 · [Module guide](../modules/05_building_tools/README.md) · [Use case](../modules/05_building_tools/use_case/booking_assistant.py) · [Tests](../modules/05_building_tools/tests)

| Feature coverage | Delivered example | AWS required / local alternative | Official reference |
|---|---|---|---|
| @tool; docstrings, parameter descriptions and type hints becoming tool specifications | [01_typed_search.py](../modules/05_building_tools/examples/01_typed_search.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/custom-tools/) |
| toolUse, toolResult, status and tool exception feedback | [02_results_and_errors.py](../modules/05_building_tools/examples/02_results_and_errors.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/custom-tools/) |
| @tool(context=True), ToolContext, private agent state and invocation state | [03_tool_context.py](../modules/05_building_tools/examples/03_tool_context.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/custom-tools/) |
| Async tools, streamed tool progress and consumption | [04_async_progress.py](../modules/05_building_tools/examples/04_async_progress.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/custom-tools/) |
| Class-based tools sharing a database connection; read-only queries | [05_resource_sharing.py](../modules/05_building_tools/examples/05_resource_sharing.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/custom-tools/) |
| TOOL_SPEC modules and direct agent.tool calls | [06_module_tools.py](../modules/05_building_tools/examples/06_module_tools.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/custom-tools/) |
| Sequential and concurrent execution; race and resource limits | [07_tool_executors.py](../modules/05_building_tools/examples/07_tool_executors.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/custom-tools/) |
| Trusted folder loading, hot reload and review before registration | [08_tool_directory.py](../modules/05_building_tools/examples/08_tool_directory.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/custom-tools/) |
| Build it yourself: bounded boto3 Converse loop with toolConfig/toolUse/toolResult, then Strands equivalent | [09_manual_converse_loop.py](../modules/05_building_tools/examples/09_manual_converse_loop.py) | Yes; offline Stubber replay | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/custom-tools/) |

## 06_community_tools: Community and vended tools

Assistant v4 · [Module guide](../modules/06_community_tools/README.md) · [Use case](../modules/06_community_tools/use_case/travel_day_helper.py) · [Tests](../modules/06_community_tools/tests)

| Feature coverage | Delivered example | AWS required / local alternative | Official reference |
|---|---|---|---|
| Supported replacements for calculator/current_time/http_request: bounded Decimal conversion, injected clock and vended HTTP; synthetic Open-Meteo fixture | [01_calculator_time_weather.py](../modules/06_community_tools/examples/01_calculator_time_weather.py) | No; live weather needs internet | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/community-tools-package/) |
| file_read, file_write, editor and shell with explicit consent and path restrictions | [02_files_and_consent.py](../modules/06_community_tools/examples/02_files_and_consent.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/community-tools-package/) |
| Vended python_repl replacement, consent gate and BYPASS_TOOL_CONSENT explanation | [03_python_with_consent.py](../modules/06_community_tools/examples/03_python_with_consent.py) | No; execution environment capability check | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/community-tools-package/) |
| Supported use_agent, vended notebook, image_reader and handoff_to_user; migration guide for retrieve/memory/think/use_llm/journal | [04_tool_catalog.py](../modules/06_community_tools/examples/04_tool_catalog.py) | Optional; AWS tool adapters use fixtures locally | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/community-tools-package/) |
| use_aws with scoped read-only role; denied write demonstration | [05_read_only_aws.py](../modules/06_community_tools/examples/05_read_only_aws.py) | Yes; recorded contract locally | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/community-tools-package/) |

Tier 1 integration: [Nimbus Booking Helper](../checkpoints/01_booking_helper/README.md) and [trajectory test](../checkpoints/01_booking_helper/test_booking_helper.py). See [supported tool migrations](../modules/06_community_tools/MIGRATIONS.md); deprecated names in this table identify replacements, not imports used by the lessons.

## 07_rag: Retrieval-augmented generation

Assistant v5 · [Module guide](../modules/07_rag/README.md) · [Use case](../modules/07_rag/use_case/ask_nimbus.py) · [Tests](../modules/07_rag/tests)

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| Markdown/PDF loading, chunk boundaries and source/page metadata | [01_load_and_chunk.py](../modules/07_rag/examples/01_load_and_chunk.py) | No | [Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| Embedding primer, cosine similarity by hand, 2D projection and its limits | [02_embeddings_by_hand.py](../modules/07_rag/examples/02_embeddings_by_hand.py) | No | [Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| Chroma persistence and Ollama embeddings; offline deterministic embedding fixture | [03_local_index.py](../modules/07_rag/examples/03_local_index.py) | No | [Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| search_policies tool, agentic retrieval, citations, grounding and abstention | [04_cited_search.py](../modules/07_rag/examples/04_cited_search.py) | No | [Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| Optional Bedrock Knowledge Base, S3 Vectors, BedrockKnowledgeBaseStore and metadata filters; infrastructure and teardown | [05_knowledge_base.py](../modules/07_rag/examples/05_knowledge_base.py) | Yes; local Chroma alternative | [Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| Titan Text Embeddings or verified equivalent; embedding-specific API versus Converse | [06_bedrock_embeddings.py](../modules/07_rag/examples/06_bedrock_embeddings.py) | Yes; Ollama alternative | [Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |

## 08_advanced_rag: Advanced retrieval and evaluation

Assistant v5 · [Module guide](../modules/08_advanced_rag/README.md) · [Use case](../modules/08_advanced_rag/use_case/retrieval_comparison.py) · [Tests](../modules/08_advanced_rag/tests)

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| Agent query rewrite and multi-query retrieval with a query budget | [01_query_rewriting.py](../modules/08_advanced_rag/examples/01_query_rewriting.py) | No | [Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| BM25 plus vector search and deduplication | [02_hybrid_search.py](../modules/08_advanced_rag/examples/02_hybrid_search.py) | No | [Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| Local overlap reranking heuristic and optional Bedrock reranking with supported model/region | [03_reranking.py](../modules/08_advanced_rag/examples/03_reranking.py) | Optional; local scoring alternative | [Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| Metadata filters and bounded multi-hop retrieval | [04_filters_multihop.py](../modules/08_advanced_rag/examples/04_filters_multihop.py) | No | [Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| Hit rate, faithfulness, correctness, held-out golden sets and LLM-as-judge limitations | [05_evaluate_retrieval.py](../modules/08_advanced_rag/examples/05_evaluate_retrieval.py) | No | [Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| Failure fixtures: missing/irrelevant evidence, rejected false citations and quarantined injection | [06_failure_gallery.py](../modules/08_advanced_rag/examples/06_failure_gallery.py) | No | [Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |

## 09_memory: Memory, state and sessions

Assistant v6 · [Module guide](../modules/09_memory/README.md) · [Use case](../modules/09_memory/use_case/preferences_assistant.py) · [Tests](../modules/09_memory/tests)

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| Stateless model versus messages and agent.state; explicitly exposing private state when needed | [01_state_and_messages.py](../modules/09_memory/examples/01_state_and_messages.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/session-management/) |
| FileSessionManager, session IDs, resume and user isolation | [02_file_sessions.py](../modules/09_memory/examples/02_file_sessions.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/session-management/) |
| S3SessionManager; moto tests and optional tagged bucket teardown | [03_s3_sessions.py](../modules/09_memory/examples/03_s3_sessions.py) | Yes; file sessions alternative | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/session-management/) |
| Preference storage, retention, retrieval and deletion of registered active data | [04_local_preferences.py](../modules/09_memory/examples/04_local_preferences.py) | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/session-management/) |
| Stable MemoryManager plus a course-owned AgentCore store; optional live scoped recall | [05_agentcore_memory.py](../modules/09_memory/examples/05_agentcore_memory.py) | Yes; local preferences alternative | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/session-management/) |
| Mem0MemoryStore via mem0-strands and MemoryManager; replace deprecated mem0_memory tool; deletion through backend API | [06_mem0_store.py](../modules/09_memory/examples/06_mem0_store.py) | No; Ollama-backed configuration | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/session-management/) |

## 10_streaming: Streaming and async

Assistant v6 · use case: `modules/10_streaming/use_case/streaming_trip_planner.py`

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| stream_async text deltas, reasoning if exposed, tool and lifecycle events versus callbacks | `modules/10_streaming/examples/01_stream_events.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/streaming/async-iterators/) |
| Concurrent agents, timeouts, cancellation and bounded resource use | `modules/10_streaming/examples/02_concurrency_and_cancel.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/streaming/async-iterators/) |
| FastAPI SSE framing, client disconnect and cancellation propagation | `modules/10_streaming/examples/03_fastapi_sse.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/streaming/async-iterators/) |
| Streamlit chat, per-user sessions and streamed responses | `modules/10_streaming/examples/04_streamlit_chat.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/streaming/async-iterators/) |

## 11_hooks: Hooks and lifecycle

Assistant v7 · use case: `modules/11_hooks/use_case/audited_booking.py`

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| HookProvider, HookRegistry; AgentInitializedEvent, Before/AfterInvocationEvent, Before/AfterModelCallEvent | `modules/11_hooks/examples/01_lifecycle_hooks.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/hooks-events/) |
| Before/AfterToolCallEvent, Before/AfterToolsEvent; block or modify inputs and rewrite results | `modules/11_hooks/examples/02_tool_hooks.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/hooks-events/) |
| MessageAddedEvent and MessageUpdatedEvent; redaction before persistence/logging | `modules/11_hooks/examples/03_message_hooks.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/hooks-events/) |
| Invocation state, structured audit trail, booking budget enforcement and metrics | `modules/11_hooks/examples/04_audit_budget.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/agents/hooks-events/) |

## 12_interrupts: Human approval with interrupts

Assistant v8 · use case: `modules/12_interrupts/use_case/refund_approval.py`

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| Interrupt an individual call or batch from supported hooks; capture identifiers | `modules/12_interrupts/examples/01_hook_interrupt.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/interrupts/) |
| Interrupt from ToolContext and resume with matched human response | `modules/12_interrupts/examples/02_tool_interrupt.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/interrupts/) |
| Approve/reject/expire refunds over $500 and non-refundable changes; handoff_to_user comparison | `modules/12_interrupts/examples/03_approval_cli.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/interrupts/) |
| Authenticated approval state, web approve/reject, audit trail and replay-safe mutation | `modules/12_interrupts/examples/04_approval_web.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/interrupts/) |

## 13_guardrails: Guardrails and safety

Assistant v9 · use case: `modules/13_guardrails/use_case/hardened_support.py`

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| Provider-independent hook checks and typed business policy | `modules/13_guardrails/examples/01_local_guardrails.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/safety-security/guardrails/) |
| Poisoned document attack, untrusted content boundary, tool authorization and regression cases | `modules/13_guardrails/examples/02_prompt_injection.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/safety-security/guardrails/) |
| Read-only SQLite, tool allow-lists and restricted use_aws role | `modules/13_guardrails/examples/03_least_privilege.py` | Optional; local tools alternative | [Documentation](https://strandsagents.com/docs/user-guide/sdk/safety-security/guardrails/) |
| Current invocation limits, tool budgets and wall-clock timeouts | `modules/13_guardrails/examples/04_limits.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/safety-security/guardrails/) |
| Content filters, denied topics, PII masking, grounding checks, BedrockModel attachment and trace; CDK lifecycle | `modules/13_guardrails/examples/05_bedrock_guardrails.py` | Yes; local policy checks with narrower coverage | [Documentation](https://strandsagents.com/docs/user-guide/sdk/safety-security/guardrails/) |

## 14_mcp: Model Context Protocol

Assistant v9 · use case: `modules/14_mcp/use_case/mcp_booking_assistant.py`

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| MCPClient stdio transport and managed/context-manager lifecycle | `modules/14_mcp/examples/01_stdio_client.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/) |
| Streamable HTTP transport, lifetime, authentication and shutdown | `modules/14_mcp/examples/02_http_client.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/) |
| Official mcp SDK server exposing Nimbus booking tools | `modules/14_mcp/examples/03_booking_server.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/) |
| Pinned AWS Documentation and AWS Pricing MCP servers via uvx; trust and access review | `modules/14_mcp/examples/04_aws_servers.py` | Optional; Pricing requires credentials, fixture alternative | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/) |
| Filter/namespace tools, combine servers and reject unexpected capabilities | `modules/14_mcp/examples/05_tool_filtering.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/) |

## 15_agents_as_tools: Agents as tools

Assistant v10 · use case: `modules/15_agents_as_tools/use_case/nimbus_concierge.py`

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| Flight, hotel and policy agents wrapped as tools | `modules/15_agents_as_tools/examples/01_specialist_tools.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agents-as-tools/) |
| Minimum specialist context, output validation and authority boundaries | `modules/15_agents_as_tools/examples/02_context_boundaries.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agents-as-tools/) |
| Compare single-agent and delegated quality, latency and total token cost | `modules/15_agents_as_tools/examples/03_delegation_cost.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agents-as-tools/) |

## 16_swarms: Swarms

Assistant v10 · use case: `modules/16_swarms/use_case/itinerary_swarm.py`

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| Swarm, entry point, agent handoffs and shared context | `modules/16_swarms/examples/01_handoffs.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/swarm/) |
| max_handoffs, max_iterations, execution_timeout, node_timeout and repetitive handoff detection | `modules/16_swarms/examples/02_swarm_limits.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/swarm/) |
| Result status, node outcomes, execution order and failure diagnosis | `modules/16_swarms/examples/03_swarm_results.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/swarm/) |
| Researcher, budget planner, itinerary writer and reviewer collaboration | `modules/16_swarms/examples/04_itinerary_team.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/swarm/) |

## 17_graphs: Graphs and workflows

Assistant v10 · use case: `modules/17_graphs/use_case/group_trip_pipeline.py`

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| GraphBuilder nodes, edges, entry point and per-node results | `modules/17_graphs/examples/01_graph_basics.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/graph/) |
| Parallel flight/hotel branches and single fan-in after completion | `modules/17_graphs/examples/02_parallel_search.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/graph/) |
| Conditional edges and bounded loops using set_max_node_executions/timeouts | `modules/17_graphs/examples/03_conditional_budget.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/graph/) |
| Nested graph/swarm nodes and aggregate limits | `modules/17_graphs/examples/04_nested_patterns.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/graph/) |
| Existing workflow tool versus Graph and deterministic orchestration | `modules/17_graphs/examples/05_workflow_comparison.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/graph/) |
| Parse, parallel search, budget branch, approval, and confirmation draft | `modules/17_graphs/examples/06_approval_pipeline.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/graph/) |

## 18_a2a: Agent-to-Agent protocol

Assistant v10 · use case: `modules/18_a2a/use_case/partner_upgrade.py`

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| A2A protocol, Strands A2AServer and agent cards | `modules/18_a2a/examples/01_partner_server.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agent-to-agent/) |
| A2AAgent endpoint, invoke_async and streamed remote results | `modules/18_a2a/examples/02_remote_agent.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agent-to-agent/) |
| client_config authenticated transport, card discovery and credential boundaries | `modules/18_a2a/examples/03_authenticated_client.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agent-to-agent/) |
| Protocol contracts for a partner in another framework; full LangGraph implementation in capstone | `modules/18_a2a/examples/04_framework_interop.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agent-to-agent/) |

## 19_observability: Observability, testing and evaluation

Assistant v10 · use case: `modules/19_observability/use_case/support_quality_gate.py`

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| AgentResult token/cycle/latency/tool metrics and total cost accounting | `modules/19_observability/examples/01_agent_metrics.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/evals-sdk/) |
| OpenTelemetry console and OTLP exporter; local Jaeger with Docker | `modules/19_observability/examples/02_local_tracing.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/evals-sdk/) |
| Scripted Model interface, tool unit tests, moto/Stubber, deprecations and opt-in live markers | `modules/19_observability/examples/03_offline_testing.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/evals-sdk/) |
| Cases, experiments, output and trajectory evaluators, LLM judges and deterministic scoring | `modules/19_observability/examples/04_strands_evals.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/evals-sdk/) |
| strands-evals run thresholds and nonzero exits as a CI quality gate | `modules/19_observability/examples/05_evaluation_cli.py` | No | [Documentation](https://strandsagents.com/docs/user-guide/evals-sdk/) |
| CloudWatch and AgentCore telemetry, redaction and retention | `modules/19_observability/examples/06_cloud_observability.py` | Yes; local console/Jaeger alternative | [Documentation](https://strandsagents.com/docs/user-guide/evals-sdk/) |
| AgentCore Evaluations as a managed option | `modules/19_observability/examples/07_managed_evaluation.py` | Yes; local Evals alternative | [Documentation](https://strandsagents.com/docs/user-guide/evals-sdk/) |

## 20_deployment: Deploying to AWS

Assistant v10 · use case: `modules/20_deployment/use_case/deployment_comparison.py`

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| Local/Lambda/Fargate/AgentCore tradeoffs; EKS and EC2 overview | `modules/20_deployment/examples/01_hosting_decision.py` | No; local workload model | [Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/using-any-agent-framework.html) |
| BedrockAgentCoreApp, @app.entrypoint and local runtime testing | `modules/20_deployment/examples/02_agentcore_local.py` | No; model can use Ollama | [Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/using-any-agent-framework.html) |
| Toolkit/CLI deploy, invoke, streaming and sessions; resource inventory and teardown | `modules/20_deployment/examples/03_agentcore_runtime.py` | Yes; local runtime alternative | [Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/using-any-agent-framework.html) |
| Lambda handler, dependency packaging, scoped execution role and CDK app | `modules/20_deployment/examples/04_lambda_handler.py` | Yes for deployment; offline handler alternative | [Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/using-any-agent-framework.html) |
| FastAPI container, Fargate service/load balancer, logs and explicit idle costs; CDK lifecycle | `modules/20_deployment/examples/05_fargate_api.py` | Yes for deployment; local container alternative | [Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/using-any-agent-framework.html) |
| Secrets Manager/SSM, per-environment configuration, roles and cleanup comparison | `modules/20_deployment/examples/06_runtime_configuration.py` | Yes; local environment configuration | [Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/using-any-agent-framework.html) |

## 21_agentcore: Amazon Bedrock AgentCore services

Assistant v11 · use case: `modules/21_agentcore/use_case/production_copilot.py`

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| Short-term events and semantic, preference, summary and episodic strategies; deletion | `modules/21_agentcore/examples/01_memory.py` | Yes; local preference store | [Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) |
| Lambda/OpenAPI to MCP, semantic tool search and scoped targets | `modules/21_agentcore/examples/02_gateway.py` | Yes; local booking MCP | [Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) |
| Cognito/JWT inbound identity and third-party OAuth outbound identity | `modules/21_agentcore/examples/03_identity.py` | Yes; local authenticated test provider | [Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) |
| AgentCore Code Interpreter tool, sessions, execution limits and cleanup | `modules/21_agentcore/examples/04_code_interpreter.py` | Yes; reviewed local computation | [Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) |
| AgentCore Browser tool, restricted destinations, sessions and cleanup | `modules/21_agentcore/examples/05_browser.py` | Yes; fixture web pages | [Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) |
| Service telemetry, redaction, permissions and retention cleanup | `modules/21_agentcore/examples/06_observability.py` | Yes; local OTLP | [Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) |
| Gateway Policy, Cedar, tool-input limits and refusal of excess refunds | `modules/21_agentcore/examples/07_policy.py` | Yes; local typed policy | [Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) |
| Managed evaluation configuration, scheduled runs, score review and schedule deletion | `modules/21_agentcore/examples/08_evaluations.py` | Yes; local evaluation runner | [Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) |
| Memory, booking Gateway, sign-in, refund policy and recurring evaluations | `modules/21_agentcore/examples/09_integrated_copilot.py` | Yes; composed local support app | [Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) |

## bonus/B1_voice: Voice agents

Assistant v11 · use case: `modules/bonus/B1_voice/use_case/voice_booking.py`

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| Stable strands.bidi.BidiAgent and compatible Nova Sonic voice session | `modules/bonus/B1_voice/examples/01_voice_session.py` | Yes for Nova; optional non-AWS voice provider | [Documentation](https://strandsagents.com/docs/user-guide/sdk/bidi/agent/) |
| Bidirectional audio, barge-in and cancellation boundaries | `modules/bonus/B1_voice/examples/02_barge_in.py` | Yes for Nova; recorded audio events locally | [Documentation](https://strandsagents.com/docs/user-guide/sdk/bidi/agent/) |
| Voice tool approval and session cleanup; Experimental OpenAI Live excluded from core | `modules/bonus/B1_voice/examples/03_voice_approval.py` | Yes for Nova; offline approval fixture | [Documentation](https://strandsagents.com/docs/user-guide/sdk/bidi/agent/) |

## bonus/B2_typescript: Strands in TypeScript

Assistant v1 · use case: `modules/bonus/B2_typescript/use_case/typescript_booking.ts`

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| TypeScript primer and first agent with environment model selection | `modules/bonus/B2_typescript/examples/01_first_agent.ts` | No | [Documentation](https://github.com/strands-agents/harness-sdk/releases/tag/typescript/v1.22.0) |
| Typed Nimbus booking tools and validation | `modules/bonus/B2_typescript/examples/02_typed_tool.ts` | No | [Documentation](https://github.com/strands-agents/harness-sdk/releases/tag/typescript/v1.22.0) |
| Provider choice, async invocation and result comparison with Python | `modules/bonus/B2_typescript/examples/03_provider_and_result.ts` | No | [Documentation](https://github.com/strands-agents/harness-sdk/releases/tag/typescript/v1.22.0) |

## bonus/B3_self_extending: Self-extending agents

Assistant v11 · use case: `modules/bonus/B3_self_extending/use_case/reviewed_tool_builder.py`

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| Current SDK tool-generation builder with constrained inventory; archived agent-builder explained as historical context | `modules/bonus/B3_self_extending/examples/01_builder.py` | No | [Documentation](https://github.com/strands-agents/agent-builder) |
| Generated source is untrusted; review, test and explicitly approve before loading | `modules/bonus/B3_self_extending/examples/02_review_generated_tool.py` | No | [Documentation](https://github.com/strands-agents/agent-builder) |
| Approved tools in an allow-listed directory, hot reload and audit history | `modules/bonus/B3_self_extending/examples/03_trusted_reload.py` | No | [Documentation](https://github.com/strands-agents/agent-builder) |

## bonus/B4_whats_new: What is new in the pinned release

Assistant v11 · use case: `modules/bonus/B4_whats_new/use_case/release_feature_lab.py`

| Feature coverage | Planned example file | AWS required / local alternative | Official reference |
|---|---|---|---|
| agent.cancel and whole-agent-tree invocation limits | `modules/bonus/B4_whats_new/examples/01_cancel_and_limits.py` | No | [Documentation](https://github.com/strands-agents/harness-sdk/releases/tag/python/v1.62.0) |
| Public middleware composition and behavior tests | `modules/bonus/B4_whats_new/examples/02_public_middleware.py` | No | [Documentation](https://github.com/strands-agents/harness-sdk/releases/tag/python/v1.62.0) |
| Stable Evals red teaming and held-out attack corpus; replace experimental imports | `modules/bonus/B4_whats_new/examples/03_stable_redteam.py` | No | [Documentation](https://github.com/strands-agents/harness-sdk/releases/tag/python/v1.62.0) |
| Experimental AgentConfig opt-in demonstration, isolated from the core route | `modules/bonus/B4_whats_new/examples/04_experimental_config.py` | No | [Documentation](https://github.com/strands-agents/harness-sdk/releases/tag/python/v1.62.0) |

## Cross-course and capstone coverage

| Deliverable | Planned implementation | Acceptance evidence |
|---|---|---|
| Provider factory and deterministic mock | `common/models.py`, `common/testing.py` | Real SDK loop; text/tool/structured/interrupt tests, no external network |
| Reproducible data | `scripts/build_data.py`, `data/manifest.json` | Counts, foreign keys, golden labels, planted incidents, PDF/image review |
| AWS inventory and cleanup | `scripts/find_leftovers.py`, each infrastructure README | Tagged resources, stack inventory, regional scan, explicit errors and unsupported-service gaps |
| Feature and content audit | `tests/test_course_structure.py`, `tests/test_links.py` | Every map target exists; required module sections/assets; internal and external links |
| Safety regression | `tests/test_iam_policies.py`, `tests/test_secret_examples.py` | Inspect synthesized IAM; reject wildcard actions and secret-like sample values |
| CloudOps Copilot | `capstones/01_cloudops_copilot/solution/main.py` | Incident detection, runbook citations, cost charts, Documentation/Pricing MCP; read-only optional live mode |
| Trip Planner Crew | `capstones/02_trip_planner_crew/solution/main.py` | Flight/hotel/weather/budget agents, graph or swarm, streaming Streamlit UI |
| Document Intelligence Pipeline | `capstones/03_document_intelligence/solution/main.py` | Receipt/image extraction, typed validation, anomaly routing, SQLite and optional DynamoDB |
| Nimbus Support Copilot | `capstones/04_nimbus_support_copilot/solution/main.py` | Booking, policy RAG, memory, interrupt approvals, Guardrails, OTLP, Evals, Runtime, Gateway and teardown |
| Partner Network | `capstones/05_partner_network/solution/main.py` | Authenticated Strands/LangGraph A2A interoperability in separate processes |
| Five tier checkpoints | `checkpoints/tier_1/README.md` through `checkpoints/tier_5/README.md` | Concrete deliverables and readiness criteria in the learning path |
| Teaching references | `docs/MENTAL_MODEL.md`, `docs/CHOOSING_THE_RIGHT_PATTERN.md`, `docs/GLOSSARY.md`, `docs/TROUBLESHOOTING.md`, `cheatsheets/` | Ecosystem diagram, two decision flowcharts, 60+ terms, real errors and five printable sheets |

## Infrastructure owners

| Lesson | CDK app / lifecycle owner (links are delivered) | Resources to price, tag and clean |
|---|---|---|
| 00 optional budget helper | `infra/budget/app.py` | Budget and notification settings; retention decision documented |
| 07 optional Knowledge Base | [infra/07_knowledge_base/app.py](../infra/07_knowledge_base/app.py) | Source bucket, S3 vector bucket/index, Knowledge Base/data source, IAM |
| 09 optional S3 sessions | [infra/09_sessions/app.py](../infra/09_sessions/app.py) | Session bucket, policies, objects and optional logs |
| 09 optional Memory (21 extends later) | [infra/09_memory/app.py](../infra/09_memory/app.py) | Memory resource with preference strategy; scoped recall-only managed policy |
| 13 optional Guardrails | `infra/guardrails/app.py` | Guardrail configuration and versions |
| 20 Lambda | `infra/lambda_support/app.py` | Function, execution role, artifact assets and logs; authenticated invocation |
| 20 Fargate | `infra/fargate_support/app.py` | Cluster/service/tasks, VPC/subnets, security groups, load balancer, ECR and logs; explicit public IPv4/network costs |
| 20 AgentCore Runtime | `infra/agentcore_runtime/app.py` | Runtime/endpoint, role, package/image assets, logs and invocation permissions |
| 21 full Copilot | `infra/agentcore_copilot/app.py` | Memory, Gateway/targets, booking Lambda, Cognito or JWT configuration, policy engine/policies, evaluation configuration/schedule, secrets and logs |
| 21 managed tools | `infra/agentcore_tools/app.py` | Browser/Code Interpreter resources and active sessions, roles and logs |
| Document capstone | `infra/document_pipeline/app.py` | DynamoDB table and scoped writer/reader permissions |

All infrastructure apps include a README, `cdk.json`, stack code, synth tests and a teardown command. Where CloudFormation lacks a needed operation, a narrowly scoped boto3 lifecycle script records resource IDs and implements symmetric create/delete. The exact supported resource coverage is verified before implementation.

Tier 2 verification: [retrieval comparison](verification/tier2_retrieval_report.json), [AWS contracts and template tests](../tests/test_tier2_cloud.py), [checkpoint tests](../checkpoints/02_policy_preferences/test_policy_preferences.py), and [resource lifecycle guide](../infra/README.md).
