# Module 15: quiz

1. Does a specialist inherit the parent history automatically here?

<details><summary>Answer</summary>

No. Its new Agent receives only the explicitly constructed public context.

</details>

2. Why validate a structured price again?

<details><summary>Answer</summary>

Pydantic checks shape and types; the catalog establishes the authoritative amount and reference.

</details>

3. Who decides the child's permissions?

<details><summary>Answer</summary>

The host selects its tools and validates the request below the model.

</details>

4. What does the 600-token fixture prove?

<details><summary>Answer</summary>

Parent-plus-child usage is counted once. It does not predict live quality or billing.

</details>

5. When is a single agent preferable?

<details><summary>Answer</summary>

When deterministic tools already solve the subtask and extra reasoning adds little value.

</details>

6. Why mark a role attempted before awaiting it?

<details><summary>Answer</summary>

Concurrent duplicate calls must not start two child models.

</details>
