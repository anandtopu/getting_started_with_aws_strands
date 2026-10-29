# Quiz

1. Why keep a PDF page number before chunking?

<details><summary>Answer</summary>

Joining pages first loses reliable page provenance; one-based PDF page numbers should come from the reader.

</details>

2. Is the toy vector plot a visualization of the real model?

<details><summary>Answer</summary>

No. It uses hand-chosen two-dimensional numbers to teach geometry; a real projection can distort neighborhoods.

</details>

3. Why not use Chroma's default embedding function?

<details><summary>Answer</summary>

It may download a model or use an unexpected provider. Explicit embeddings make behavior and cost visible.

</details>

4. Can query and corpus vectors use different models of the same dimension?

<details><summary>Answer</summary>

No. Equal length does not mean their dimensions have the same meaning.

</details>

5. Does an exact quote make an answer faithful?

<details><summary>Answer</summary>

Not necessarily. The quote may be real while the surrounding claim misinterprets it.

</details>

6. Why use InvokeModel for Titan embeddings?

<details><summary>Answer</summary>

Converse handles chat, not embedding inference. This documented embedding-specific request is intentional.

</details>
