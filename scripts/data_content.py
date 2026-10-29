"""Original synthetic policies and places; all commercial terms are fictional."""

PLACES = [
    ("Chicago", "United States"),
    ("Seattle", "United States"),
    ("Boston", "United States"),
    ("Austin", "United States"),
    ("Denver", "United States"),
    ("Portland", "United States"),
    ("Toronto", "Canada"),
    ("Vancouver", "Canada"),
    ("Montreal", "Canada"),
    ("Mexico City", "Mexico"),
    ("Lisbon", "Portugal"),
    ("Porto", "Portugal"),
    ("Madrid", "Spain"),
    ("Barcelona", "Spain"),
    ("Paris", "France"),
    ("Lyon", "France"),
    ("Rome", "Italy"),
    ("Florence", "Italy"),
    ("Berlin", "Germany"),
    ("Munich", "Germany"),
    ("Amsterdam", "Netherlands"),
    ("Copenhagen", "Denmark"),
    ("Stockholm", "Sweden"),
    ("Oslo", "Norway"),
    ("Tokyo", "Japan"),
    ("Kyoto", "Japan"),
    ("Seoul", "South Korea"),
    ("Sydney", "Australia"),
    ("Melbourne", "Australia"),
    ("Auckland", "New Zealand"),
]

POLICIES = {
    "cancellation": (
        "Cancellation",
        "POL-CAN-001",
        [
            "All amounts are USD. These rules govern only synthetic Nimbus bookings.",
            "A booking cancelled within 24 hours after creation receives a full refund, "
            "provided departure is at least 7 days after booking creation. Both conditions apply.",
            "After that window, a flexible flight can be cancelled before departure for a "
            "$25 cancellation fee per traveler. A non-refundable flight receives no cash refund.",
            "A hotel marked flexible can be cancelled without charge at least 48 hours before "
            "check-in. A later cancellation costs one night's room charge. Non-refundable "
            "hotel reservations receive no refund outside the 24-hour booking exception.",
            "The booking time is stored in UTC. The departure and check-in deadlines in the "
            "fixture also use UTC so the exercises have one unambiguous clock.",
        ],
    ),
    "refund": (
        "Refund",
        "POL-REF-001",
        [
            "An eligible refund returns to the original synthetic payment method within "
            "5 to 10 business days after approval. A refund cannot exceed the amount paid.",
            "The full-refund exception is cancellation within 24 hours of booking creation "
            "when departure is at least 7 days after creation. See POL-CAN-001.",
            "Refunds over $500 require supervisor approval before any payment operation. "
            "Exactly $500 does not trigger that threshold; other authorization checks still apply.",
            "A denied or expired approval never creates a refund. Approval expires after "
            "30 minutes. A repeated request with the same idempotency key returns the "
            "original outcome rather than sending a second refund.",
            "The sum of all partial refunds cannot exceed the original captured payment. "
            "Nimbus records the amount, reason, approving actor and UTC timestamp.",
        ],
    ),
    "change_fee": (
        "Changes and fees",
        "POL-CHG-001",
        [
            "A standard flight change costs $75 per traveler plus any positive fare difference. "
            "A flexible fare has no change fee, but a positive fare difference still applies.",
            "Flight changes must be requested at least 12 hours before departure. Changes "
            "inside that deadline are refused by the teaching booking system.",
            "Changing a non-refundable fare always needs supervisor approval. Approval "
            "does not waive the $75 fee or the fare difference unless explicitly recorded.",
            "A requested change is a quote until the traveler accepts the final total. "
            "If inventory is exhausted, the original booking stays intact.",
        ],
    ),
    "baggage": (
        "Baggage",
        "POL-BAG-001",
        [
            "Each synthetic Nimbus flight includes one cabin bag up to 8 kg and one "
            "personal item up to 3 kg per traveler.",
            "The first checked bag costs $30 each way and may weigh at most 23 kg. "
            "A second checked bag costs $45 each way, with the same 23 kg limit.",
            "A checked bag over 23 kg and up to 32 kg incurs an additional $60 charge. "
            "Items above 32 kg are not accepted by the synthetic booking policy.",
            "These are fictional commercial limits for course exercises, not guidance "
            "for any real airline or journey.",
        ],
    ),
    "travel_insurance": (
        "Optional travel protection",
        "POL-INS-001",
        [
            "Nimbus Demo Protection is a fictional add-on for data-processing exercises. "
            "It costs $18 per traveler per trip and has a $50 simulated deductible.",
            "The training policy caps a simulated claim at $2,000. Buying the add-on "
            "does not guarantee a claim will be accepted and does not change flight fare rules.",
            "This document provides no insurance, health, legal or eligibility advice. "
            "The assistant must not invent real coverage or recommend a policy to a traveler.",
            "Protection is opt-in. The system records explicit consent and never adds "
            "the $18 charge automatically.",
        ],
    ),
    "privacy": (
        "Privacy and retention",
        "POL-PRI-001",
        [
            "All course identities and transactions are fabricated. Do not enter real "
            "passport numbers, payment cards, passwords or customer data into these lessons.",
            "Local conversation history is retained for 30 days by the teaching policy. "
            "Travel preferences expire after 90 days unless the synthetic user renews consent.",
            "A deletion request removes the user's local conversation and preference "
            "records within 24 hours in the simulated workflow. Deletion includes indexes "
            "and cached preference copies, not just the user-facing display.",
            "Audit logs contain a synthetic actor ID, action, result and time. Raw passport-like "
            "and card-like strings are redacted before logging. Audit retention is 7 days.",
            "Memory is scoped to a user and purpose. A tool must not fetch another user's "
            "preferences merely because a model asks it to.",
        ],
    ),
}

RUNBOOKS = {
    "incident_response": """# Nimbus incident response
Synthetic runbook OPS-INC-001. Acknowledge a critical incident within 5 minutes.
1. Identify the service and UTC window; compare p95 latency with the 800 ms target.
2. Check error rate against the 2% threshold and correlate deployment versions.
3. Separate a dependency timeout from a slow database by checking dependency_ms.
4. Propose a reversible mitigation; an operator approves every production mutation.
5. Record evidence, timeline, customer effect and a follow-up owner. Never paste raw PII.
""",
    "deployments": """# Nimbus deployments
Synthetic runbook OPS-DEP-001. Roll out to 10% of traffic for 15 minutes.
Stop the rollout if errors exceed 2% or p95 latency exceeds 800 ms for 5 minutes.
Correlate errors with deployment_id. Prepare a rollback to the prior known-good version.
The assistant can draft a rollback command but cannot execute it without operator approval.
Compare health metrics for 15 minutes after rollback and attach the incident evidence.
""",
    "on_call": """# Nimbus on-call
Synthetic runbook OPS-ONC-001. Critical: acknowledge in 5 minutes; high: 30 minutes.
Normal support tickets have a 24-hour response target. Ask for a synthetic booking ID.
For a departure within 24 hours, route a booking-blocking problem as high priority.
Page the secondary fictional operator after 10 minutes without acknowledgment.
Escalate refunds over $500 to a supervisor. Keep approval decisions separate from diagnosis.
""",
    "cost_reviews": """# Nimbus cost reviews
Synthetic runbook OPS-CST-001. Review 90 days of usage and compare the latest 7 days
with the previous 28 days. Flag daily spend above twice the historical daily mean.
Inspect NAT gateways with zero data transfer, compute with CPU below 5% for 14 days,
and Lambda invocation or duration spikes. Quote savings assumptions and observation windows.
Propose changes only. A read-only analysis role cannot delete or resize infrastructure.
Include logs, load balancers, storage, public IPv4 addresses and retained deployment assets.
""",
}
