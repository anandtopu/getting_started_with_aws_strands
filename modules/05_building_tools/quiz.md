# Module 05 quiz

1. Is a type hint enough to authorize a booking lookup?

<details><summary>Answer</summary>

No. Check ownership using a trusted application identity.

</details>

2. Who supplies tool_context?

<details><summary>Answer</summary>

The framework injects it; it is omitted from the model-visible input schema.

</details>

3. What does the last async tool yield mean?

<details><summary>Answer</summary>

It becomes the final tool result; preceding yields can be consumed as progress.

</details>

4. Are direct agent.tool calls guaranteed to use the calling thread?

<details><summary>Answer</summary>

No. The pinned SDK can execute them across an async/thread boundary.

</details>

5. Can concurrent tools share a writable SQLite handle without coordination?

<details><summary>Answer</summary>

No. Use suitable transaction/concurrency design; these lessons use read-only queries.

</details>

6. Why is folder loading risky?

<details><summary>Answer</summary>

Importing Python runs it. A model-written file must not be registered without independent review.

</details>
