# Quiz

1. Does a $500 refund need approval under this demo policy?

<details><summary>Answer</summary>

No; refunds strictly above $500 do. Changes to non-refundable fares require approval independently.

</details>

2. What binds a decision to an operation?

<details><summary>Answer</summary>

The stored request ID, customer, booking, action, amount and expiry.

</details>

3. Is an interrupt response of approve sufficient?

<details><summary>Answer</summary>

No. Financial actions require a recorded supervisor decision and transactional revalidation.

</details>

4. What happens at exactly expires?

<details><summary>Answer</summary>

The request is expired; now must be strictly less than expires.

</details>

5. What does a repeated successful apply return?

<details><summary>Answer</summary>

already_applied, with no second refund.

</details>

6. What survives a demo web restart?

<details><summary>Answer</summary>

The SQLite ledger survives; the paused Agent and resumable in-memory mapping do not.

</details>

