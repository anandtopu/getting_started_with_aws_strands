# Module 01 quiz

1. Which model does bare Agent use in this pin?

<details><summary>Answer</summary>

The Bedrock default constant is global.anthropic.claude-sonnet-4-6. The course overrides it; future pins can change it.

</details>

2. Is str(result) the entire result?

<details><summary>Answer</summary>

No. Inspect message, stop_reason and metrics too.

</details>

3. Does a callback select tools?

<details><summary>Answer</summary>

No. It observes events; the model selects and the framework executes tools.

</details>

4. Where does a tool result appear?

<details><summary>Answer</summary>

In a user-role message containing a toolResult content block before the next model call.

</details>

5. Why use callback_handler=None?

<details><summary>Answer</summary>

To avoid the default printer when the application renders the final result itself.

</details>

6. Does a policy prompt guarantee grounding?

<details><summary>Answer</summary>

No. Test supported and unanswerable questions; a model can still ignore its instructions.

</details>
