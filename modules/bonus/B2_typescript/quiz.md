# TypeScript quiz

1. Why await invoke?

<details><summary>Answer</summary>

The model and tools may complete asynchronously.

</details>

2. Do TypeScript types validate model arguments?

<details><summary>Answer</summary>

No. Use the runtime Zod schema.

</details>

3. Why integer cents?

<details><summary>Answer</summary>

To avoid floating point money arithmetic.

</details>

4. Can this tool book a flight?

<details><summary>Answer</summary>

No; its output is a quote and booked is false.

</details>

5. How does mock mode test the real SDK?

<details><summary>Answer</summary>

A scripted Model emits real SDK events; Agent performs tool dispatch.

</details>

6. Where does provider selection belong?

<details><summary>Answer</summary>

The common.ts getModel factory, the language-equivalent shared boundary.

</details>
