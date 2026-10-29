# Third-party notices

Course text, synthetic data, and original implementation are covered by the repository's MIT license. Installed dependencies retain their own licenses; installation does not relicense them.

`common/testing.py` follows the event-stream pattern demonstrated by the Apache-2.0-licensed Strands Agents SDK [mocked model fixture](https://github.com/strands-agents/harness-sdk/blob/python/v1.62.0/strands-py/tests/fixtures/mocked_model_provider.py). The local implementation adds explicit response scripts, exhaustion errors, configuration copies, token counts, cancellation checks and validated structured output. Attribution: Amazon.com, Inc. or its affiliates and Strands Agents contributors. See the upstream [license](https://github.com/strands-agents/harness-sdk/blob/python/v1.62.0/strands-py/LICENSE).

The course does not bundle model weights. Models downloaded through Ollama have their own licenses and hardware requirements. AWS, Amazon Bedrock, Amazon Bedrock AgentCore, Strands Agents, Anthropic, OpenAI, Ollama, and GitHub names identify the relevant products; this course does not claim endorsement by their owners.

All people, bookings, airlines, hotels, policies, receipts, logs, and transactions in `data/` are invented for teaching. Real destination names are geographic labels, not travel recommendations. The malicious document is an explicitly labelled security fixture and must never be treated as trusted instructions.
