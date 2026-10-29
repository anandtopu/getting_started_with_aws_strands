# Quiz

1. Why create a fresh Agent for each request?

<details><summary>Answer</summary>

To prevent one traveler inheriting another traveler's conversation.

</details>

2. Does Runtime session isolation provide application memory here?

<details><summary>Answer</summary>

No. The support core is stateless; persistence must be deliberately implemented.

</details>

3. Why does an idle Fargate deployment cost money?

<details><summary>Answer</summary>

The task, ALB and public IPv4 addresses remain allocated.

</details>

4. Why exclude .env from the image context?

<details><summary>Answer</summary>

Credentials and local profiles belong in runtime configuration, not layers or source assets.

</details>

5. Why must the ALB certificate match your DNS name?

<details><summary>Answer</summary>

HTTPS clients verify the requested hostname against the certificate.

</details>

6. What does local ASGI validation leave untested?

<details><summary>Answer</summary>

Image builds, deployment permissions, load balancing, regional service behavior, scale and real billing.

</details>
