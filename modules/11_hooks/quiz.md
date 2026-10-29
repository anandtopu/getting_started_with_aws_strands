# Quiz

1. Who supplies the trusted budget?

<details><summary>Answer</summary>

The authenticated application through invocation_state; never the model.

</details>

2. Which hook blocks an individual tool?

<details><summary>Answer</summary>

BeforeToolCallEvent, by setting cancel_tool.

</details>

3. Why normalize before the catalog lookup?

<details><summary>Answer</summary>

The policy and tool must agree on the same canonical destination.

</details>

4. Does observing MessageAddedEvent automatically change saved history?

<details><summary>Answer</summary>

No. This observer redacts its own audit copy; persistence ordering needs a separate verified integration.

</details>

5. Does every invocation emit tool events?

<details><summary>Answer</summary>

No. A model can answer without selecting a tool.

</details>

6. Why check authorization again in the tool or database?

<details><summary>Answer</summary>

A hook protects this invocation path; the underlying write must remain safe when called by another path.

</details>

