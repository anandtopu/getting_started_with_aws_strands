# Glossary

Beginner definitions for the Nimbus course. See the [feature map](FEATURE_MAP.md) for working examples.

| Term | Meaning |
|---|---|
| **A2A** | Agent-to-Agent protocol for discovering another agent and exchanging tasks and results. |
| **API** | A defined interface through which programs exchange requests and responses. |
| **Agent** | A program that asks a model to choose steps and uses tools to carry them out. |
| **Agent card** | A partner's description of its capabilities and supported protocol; not proof of trust. |
| **Agent loop** | The repeated model-call, tool-execution and result-feedback cycle managed by Strands. |
| **AgentCore** | AWS services for hosting, connecting, securing and observing agent applications. |
| **AgentCore Browser** | A managed browser session an agent can operate through tools. |
| **AgentCore Evaluations** | Managed evaluation of agent behavior using configured evaluators. |
| **AgentCore Gateway** | A service that exposes configured APIs or functions as tools. |
| **AgentCore Identity** | Identity and credential capabilities for agent access and integrations. |
| **AgentCore Memory** | A managed store for conversation events and extracted long-term records. |
| **AgentCore Policy** | A policy enforcement service used with Gateway to constrain tool access. |
| **AgentCore Runtime** | Managed hosting for an agent application; deploying code does not prove its quality. |
| **AgentResult** | The returned response together with stop reason, metrics and optional structured output. |
| **Amazon Bedrock** | An AWS service for calling supported foundation models and related managed features. |
| **Async** | A programming style that lets other work proceed while an operation waits. |
| **Authentication** | Checking who the caller is. |
| **Authorization** | Checking what that caller is allowed to do. |
| **Await** | Pause the current asynchronous task until a result is ready. |
| **Barge-in** | A person interrupting an ongoing voice response; queued playback must stop. |
| **BidiAgent** | The Strands agent for bidirectional sessions where input and output can overlap. |
| **Budget alert** | A notification about spending; it does not automatically stop charges. |
| **CDK** | AWS Cloud Development Kit: code that produces CloudFormation infrastructure templates. |
| **Callback** | Application code invoked when the SDK reports an event. |
| **CloudFormation** | AWS's service for creating and deleting declared resource stacks. |
| **CloudWatch** | AWS logs, metrics and monitoring services. |
| **Code Interpreter** | A managed execution environment for code and data tasks. |
| **Context window** | The amount of input and output a model can consider in one call. |
| **Conversation manager** | A component that trims or summarizes messages to control context size. |
| **Converse API** | Bedrock's common message interface for supported conversational models. |
| **Cross-region inference profile** | A configured route that can serve model requests in more than one region. |
| **Embedding** | A numeric representation used to compare the meaning of pieces of content. |
| **Evaluation** | Measuring behavior against cases and explicit criteria. |
| **Evaluator** | Code or a model that scores an evaluation case. |
| **Golden set** | A set of examples with independently specified expected answers or actions. |
| **Graph** | A workflow whose nodes run according to explicit edges and dependencies. |
| **Grounding** | Connecting an answer to supplied evidence rather than unsupported invention. |
| **Guardrail** | A configurable content or topic check; it is not a substitute for authorization. |
| **Hallucination** | A generated statement that is unsupported or false despite sounding plausible. |
| **Hook** | Code that reacts to a particular point in the agent lifecycle. |
| **IAM** | AWS Identity and Access Management, which controls permissions for identities and resources. |
| **Idempotency** | Making retries of the same operation avoid repeating its side effects. |
| **Identity Center** | AWS's workforce sign-in service, commonly used with temporary SSO credentials. |
| **Inference** | Running a model on input to produce output. |
| **Interrupt** | An SDK pause that returns control to the host, such as to request human approval. |
| **Invocation limit** | A bound on work, such as the number of model turns in an invocation. |
| **JSON** | A text format for structured values: objects, arrays, strings, numbers and booleans. |
| **JWT** | A signed token with claims; validate its issuer, audience, signature and expiry. |
| **Knowledge Base** | A managed retrieval system that indexes sources and retrieves relevant evidence. |
| **LLM** | A large language model that predicts and generates sequences of tokens. |
| **Lambda** | AWS compute that runs functions on demand, with execution and packaging limits. |
| **Latency** | The time a request takes to produce its result. |
| **Least privilege** | Granting only the actions and resources a particular task needs. |
| **LiteLLM** | An adapter layer that presents a common interface to multiple model services. |
| **MCP** | Model Context Protocol: a standard for exposing tools, resources and prompts to clients. |
| **MCP lifecycle** | The period during which a connected client and its transport are alive and usable. |
| **Middleware** | Code around a model or tool stage that forwards, inspects or transforms its events. |
| **Mock model** | A deterministic provider used to test application behavior without a live model. |
| **Multimodal** | Accepting or producing more than text, such as images or audio. |
| **OAuth** | A protocol for delegated access; it does not mean sharing a user's password with an agent. |
| **OTLP** | The OpenTelemetry protocol used to send telemetry to a collector. |
| **Ollama** | Software for running supported models locally on your machine. |
| **OpenTelemetry** | A standard ecosystem for collecting traces, metrics and logs. |
| **Prompt** | Instructions and input supplied to a model. |
| **Prompt caching** | Reusing supported prompt processing to reduce repeated work; pricing is model-specific. |
| **Prompt injection** | Untrusted content attempting to override the application's instructions or authority. |
| **Provider** | The adapter that translates the SDK model interface into a particular service or local model. |
| **Pydantic** | A Python library that validates actual data against declared schemas. |
| **RAG** | Retrieval-augmented generation: retrieve evidence before asking a model to answer. |
| **Red teaming** | Deliberately testing adversarial inputs to find failures; passing a corpus is not proof of safety. |
| **Redaction** | Removing or masking sensitive content before storage, logging or display. |
| **Reranking** | Reordering retrieved candidates using a second relevance score. |
| **Resource ARN** | An AWS resource identifier used to scope requests and permissions. |
| **Session** | A bounded conversation context whose storage and access need clear ownership. |
| **Sliding window** | A conversation strategy that keeps a limited recent set of messages. |
| **Span** | A timed operation within a trace, such as one model or tool call. |
| **State** | Application data retained across steps; it should not be confused with natural-language memory. |
| **Streaming** | Delivering output in pieces as it becomes available. |
| **Structured output** | A model response constrained and validated against a schema. |
| **Swarm** | A team of agents that can hand work to one another within host-defined limits. |
| **System prompt** | High-priority application guidance supplied to the model; not an access-control mechanism. |
| **Temperature** | A model setting that changes sampling variability, when the provider supports it. |
| **Token** | A model's unit of text or other encoded input/output; not necessarily a word. |
| **Tool** | A function or service capability the host explicitly makes available to an agent. |
| **Tool consent** | Human permission to use a risky tool; keep it enabled where the tool requires it. |
| **ToolResult** | The message block carrying a tool's output back to the model. |
| **ToolUse** | A model message requesting a named tool with arguments; the host must validate the request. |
| **Trace** | Connected spans describing the path of one request through a system. |
| **Vector store** | An index for searching embeddings by similarity. |
| **Zod** | A TypeScript library that validates runtime values against schemas. |
