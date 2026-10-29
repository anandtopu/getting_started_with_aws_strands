# Module 18: quiz

1. What is an agent card?

<details><summary>Answer</summary>

Service metadata describing capabilities, endpoint, protocol version and authentication requirements.

</details>

2. Does advertising bearer authentication enforce it?

<details><summary>Answer</summary>

No. HTTP middleware must check it on discovery and RPC.

</details>

3. Why use agent_factory?

<details><summary>Answer</summary>

Each context needs its own Agent/history; the shared-agent constructor is deprecated.

</details>

4. Which protocol does this pinned combination advertise?

<details><summary>Answer</summary>

A2A 0.3.0, using a2a-sdk 0.3.26 with Strands 1.62.

</details>

5. Does A2A require the partner to use Strands?

<details><summary>Answer</summary>

No. The lesson calls an actual LangGraph adapter through the same wire contract.

</details>

6. Can missing remote tokens be treated as zero?

<details><summary>Answer</summary>

No. Report unknown remote usage and keep local metrics explicitly scoped.

</details>
