# Module 03 quiz

1. Is agent.messages durable memory?

<details><summary>Answer</summary>

No. It is current in-process conversation history unless a later persistence mechanism saves it.

</details>

2. Does a sliding window guarantee a token count?

<details><summary>Answer</summary>

No. It primarily bounds messages; individual attachments or tool outputs can still be large.

</details>

3. Can a summary lose the budget?

<details><summary>Answer</summary>

Yes. Test important facts and use explicit application state for authoritative values.

</details>

4. How does the image reach the model?

<details><summary>Answer</summary>

As an image block containing format and bytes.

</details>

5. Why label extracted PDF pages?

<details><summary>Answer</summary>

So a cited answer can be checked against the original page.

</details>

6. Can every provider accept a native PDF?

<details><summary>Answer</summary>

No. Use text extraction as the common path and the native flag only with a supported model.

</details>
