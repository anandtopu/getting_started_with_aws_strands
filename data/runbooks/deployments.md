# Nimbus deployments
Synthetic runbook OPS-DEP-001. Roll out to 10% of traffic for 15 minutes.
Stop the rollout if errors exceed 2% or p95 latency exceeds 800 ms for 5 minutes.
Correlate errors with deployment_id. Prepare a rollback to the prior known-good version.
The assistant can draft a rollback command but cannot execute it without operator approval.
Compare health metrics for 15 minutes after rollback and attach the incident evidence.
