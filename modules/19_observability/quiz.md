# Quiz

1. Do 240 mock tokens estimate a live bill?

<details><summary>Answer</summary>

No. They verify accounting using fixed model-interface fixtures.

</details>

2. Why are metrics and quality separate?

<details><summary>Answer</summary>

A fast successful request can still contain an incorrect answer.

</details>

3. Why start a new tracing process?

<details><summary>Answer</summary>

The OpenTelemetry provider and SDK tracer are process-global.

</details>

4. Can a scripted judge establish helpfulness?

<details><summary>Answer</summary>

No; it exercises the judge API, not independent judgment.

</details>

5. Why does the bad fixture score 0.5?

<details><summary>Answer</summary>

Tool use passes while policy evidence fails; the any-failure CI gate still rejects it.

</details>

6. Can redacted numeric spans feed a semantic judge?

<details><summary>Answer</summary>

No. Review synthetic content-bearing traces separately and obtain appropriate data handling approval.

</details>
