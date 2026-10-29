# Quiz

1. Why not add BM25 scores to cosine scores?

<details><summary>Answer</summary>

They are not calibrated to one scale. Reciprocal rank fusion is an explicit alternative.

</details>

2. Can a reranker fix missing candidates?

<details><summary>Answer</summary>

No. Improve the first retrieval stage or increase a bounded candidate pool.

</details>

3. Is a metadata filter an authorization system?

<details><summary>Answer</summary>

Only if trusted application identity determines it and the backend enforces it. A model-selectable topic is not customer authorization.

</details>

4. What is source hit rate @3?

<details><summary>Answer</summary>

The fraction of answerable questions whose expected source appears among the top three retrieved chunks.

</details>

5. Why exclude abstention questions from that denominator?

<details><summary>Answer</summary>

They have no expected source; their behavior belongs in a separate answer/abstention metric.

</details>

6. What if the new strategy ties or regresses?

<details><summary>Answer</summary>

Report it. Use a separate development set to diagnose changes and freeze a fresh test set before tuning.

</details>
