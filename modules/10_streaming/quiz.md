# Quiz

1. Why can the browser show text before the final AgentResult?

<details><summary>Answer</summary>

Text deltas arrive during the model stream; the final result arrives when the invocation completes.

</details>

2. Should tool arguments be displayed as text?

<details><summary>Answer</summary>

No. Select public text explicitly; arguments can contain sensitive or untrusted data.

</details>

3. What does a semaphore bound?

<details><summary>Answer</summary>

The number of concurrent jobs inside its guarded section, not tokens per job.

</details>

4. Can two requests invoke the same Agent concurrently?

<details><summary>Answer</summary>

Use separate agents or serialize access; messages and invocation state are mutable conversation data.

</details>

5. Does client disconnect guarantee a remote write stopped?

<details><summary>Answer</summary>

No. Inspect authoritative state and use idempotency to handle an uncertain outcome.

</details>

6. Why renew a scripted response for each Streamlit turn?

<details><summary>Answer</summary>

The finite mock provider otherwise exhausts its script. Renew the response while preserving only that session's history.

</details>

