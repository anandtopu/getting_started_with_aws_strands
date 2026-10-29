# Module 00 quiz

1. Does parsing .env verify a model call?

<details><summary>Answer</summary>

No. Service readiness and actual inference are separate checks.

</details>

2. Does a budget alert cap spending?

<details><summary>Answer</summary>

No. It is a delayed notification, so use small workloads and clean up.

</details>

3. Are 100 tokens always 100 words?

<details><summary>Answer</summary>

No. Tokenization breaks text into model-specific pieces.

</details>

4. Which path needs no AWS account?

<details><summary>Answer</summary>

Ollama for local inference; scripted mode also needs no downloaded model.

</details>

5. What is the difference between Bedrock and Strands?

<details><summary>Answer</summary>

Bedrock hosts models; Strands is the application library that orchestrates model/tool conversations.

</details>

6. Why use SSO?

<details><summary>Answer</summary>

It supplies temporary credentials without putting long-lived AWS keys in this repository.

</details>
