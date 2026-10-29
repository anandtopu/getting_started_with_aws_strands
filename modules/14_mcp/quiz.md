# Quiz

1. Does --mock replace the local MCP transport?

<details><summary>Answer</summary>

No. It scripts model responses while the real child process and protocol run.

</details>

2. When can the client context close?

<details><summary>Answer</summary>

After discovery and all invocations using its tools have completed.

</details>

3. What name does a direct call use?

<details><summary>Answer</summary>

The original server tool name, such as search_flights, without the agent-facing prefix.

</details>

4. Does tool filtering sandbox a subprocess?

<details><summary>Answer</summary>

No. It narrows the interface visible to the agent; process permissions still matter.

</details>

5. What happens when the same booking key is reused for another flight?

<details><summary>Answer</summary>

The server rejects the changed terms instead of silently creating another reservation.

</details>

6. Why is a pricing first page insufficient for a quote?

<details><summary>Answer</summary>

It may omit products or tiers and can mix units/categories. Validate filters and follow relevant pagination before selecting rates.

</details>

