# Nimbus incident response
Synthetic runbook OPS-INC-001. Acknowledge a critical incident within 5 minutes.
1. Identify the service and UTC window; compare p95 latency with the 800 ms target.
2. Check error rate against the 2% threshold and correlate deployment versions.
3. Separate a dependency timeout from a slow database by checking dependency_ms.
4. Propose a reversible mitigation; an operator approves every production mutation.
5. Record evidence, timeline, customer effect and a follow-up owner. Never paste raw PII.
