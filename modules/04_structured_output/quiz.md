# Module 04 quiz

1. Which API replaces Agent.structured_output()?

<details><summary>Answer</summary>

Use structured_output_model on the Agent or call, then result.structured_output.

</details>

2. What does an optional hotel_id mean?

<details><summary>Answer</summary>

It may be absent/None; a present value must match the declared pattern.

</details>

3. Do positive prices prove a correct itinerary?

<details><summary>Answer</summary>

No. Validate IDs and prices against authoritative inventory.

</details>

4. What happens when repairs never succeed?

<details><summary>Answer</summary>

A bounded call stops; the application must reject missing structured output.

</details>

5. What does mock triage accuracy measure?

<details><summary>Answer</summary>

The fixture prediction/scoring pipeline, not real model quality.

</details>

6. Should golden labels be included in the prompt?

<details><summary>Answer</summary>

No. Predict first, compare afterward.

</details>
