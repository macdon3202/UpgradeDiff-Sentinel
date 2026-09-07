# Superseded deployments

## V1 — `0x7B81979993e344FA5c0A2F291c7A65BC429e960b`

- Network: Studionet
- Config readback: `UPGRADE_DIFF_SENTINEL_V1`, canonical GitHub origins,
  `max_attempts = 3`, all counters zero.
- Status: superseded before any assessment was created.
- Reason: the V1 schema required a manifest fetched from the target commit to
  contain that same target commit SHA. A Git commit SHA depends on its content,
  so this creates a cryptographic self-reference and cannot be satisfied by a
  normal reproducible Git workflow.
- State impact: none; readback showed zero assessments and zero verdict counts.

V2 resolves this by sealing a distinct manifest-attestation commit created
after the target commit is known. V1 must not be cited as successful lifecycle
evidence.
