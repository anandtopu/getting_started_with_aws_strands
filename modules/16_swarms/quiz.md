# Module 16: quiz

1. Who chooses the next node in a swarm?

<details><summary>Answer</summary>

The active model selects handoff_to_agent; the runtime validates and limits execution.

</details>

2. What travels in the handoff context?

<details><summary>Answer</summary>

Explicit shared task information. This lesson supplies public draft facts only.

</details>

3. Why can max_handoffs=2 stop after two node visits here?

<details><summary>Answer</summary>

The pinned implementation checks history length; verify semantics rather than inferring them from the name.

</details>

4. Does execution_timeout interrupt a slow final node?

<details><summary>Answer</summary>

Not by itself in this version; use node_timeout and an outer asyncio.timeout.

</details>

5. Can you add parent and all nested result usage?

<details><summary>Answer</summary>

No. Multi-agent results already aggregate children; revisits also have a documented cumulative-accounting caveat.

</details>

6. Does a reviewer's message authorize booking?

<details><summary>Answer</summary>

No. Spending requires application-owned validation and recorded human approval.

</details>
