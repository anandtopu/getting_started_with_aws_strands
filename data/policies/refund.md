# Nimbus Refund policy

POL-REF-001 | Synthetic edition 2027-01-01 | USD

An eligible refund returns to the original synthetic payment method within 5 to 10 business days after approval. A refund cannot exceed the amount paid.

The full-refund exception is cancellation within 24 hours of booking creation when departure is at least 7 days after creation. See POL-CAN-001.

Refunds over $500 require supervisor approval before any payment operation. Exactly $500 does not trigger that threshold; other authorization checks still apply.

A denied or expired approval never creates a refund. Approval expires after 30 minutes. A repeated request with the same idempotency key returns the original outcome rather than sending a second refund.

The sum of all partial refunds cannot exceed the original captured payment. Nimbus records the amount, reason, approving actor and UTC timestamp.
