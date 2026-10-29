# Quiz

1. Does agent.state automatically reach the provider?

<details><summary>Answer</summary>

No. The application must deliberately include selected state in a prompt or tool result.

</details>

2. Does a session ID authenticate a user?

<details><summary>Answer</summary>

No. Derive the namespace from already authenticated identity and enforce backend access.

</details>

3. When does a preference expire?

<details><summary>Answer</summary>

At the expiry instant: reads retain only expires > now.

</details>

4. Does clearing messages delete durable sessions?

<details><summary>Answer</summary>

No. Delete registered session data and separate preference stores explicitly.

</details>

5. Why can this AgentCore example not save the conversation?

<details><summary>Answer</summary>

The custom store is read-only, extraction and write tools are disabled, and it implements only RetrieveMemoryRecords.

</details>

6. Does Mem0 delete_all prove all data is erased?

<details><summary>Answer</summary>

It removes scoped active memories. History databases, snapshots and backups need separate erasure; this disposable demo removes its local directory on exit.

</details>
