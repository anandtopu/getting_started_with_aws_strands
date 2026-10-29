# Module 02 quiz

1. Does switching provider guarantee vision support?

<details><summary>Answer</summary>

No. Capability depends on the selected model and adapter.

</details>

2. Why leave MODEL_ID blank for the one-line switch?

<details><summary>Answer</summary>

A nonempty override wins over every provider-specific default.

</details>

3. Why is an unknown price displayed as unknown?

<details><summary>Answer</summary>

Treating it as zero would hide billable usage.

</details>

4. Does CacheConfig auto add Nova checkpoints in SDK 1.62?

<details><summary>Answer</summary>

No. Auto recognizes Anthropic IDs; the Nova lesson adds an explicit system checkpoint.

</details>

5. Why exclude high-effort Nova reasoning here?

<details><summary>Answer</summary>

It requires removing token/temperature settings and can produce very large outputs; the beginner example uses low effort.

</details>

6. What does the custom model implement?

<details><summary>Answer</summary>

Configuration access/update, streamed content events, and the required structured-output interface; unsupported features fail explicitly.

</details>
