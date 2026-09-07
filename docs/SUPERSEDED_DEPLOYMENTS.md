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

## V2 — `0xC8c4F8030D0c7A71Bfd3b1340771Dc3eCab1a747`

- Config readback passed before writes.
- Assessment 0 was created and finalized from canonical GitHub resources.
- Wrong-caller negative call finalized with expected execution error and did
  not mutate the sealed record.
- Evaluation finalized successfully but deterministically returned
  `INCOMPATIBLE / COMPARE_BINDING_FAILED`.
- Root cause: V2 required a non-existent `head_commit` property in GitHub's
  real Compare API response. Target identity was already reproducibly present
  as the final item in the complete `commits` list.
- V2 receipts:
  - create: `0xee571146e0b69bb22ef06250af0daefc83bdaed51176951365e1813efb651c39`
  - wrong caller: `0x754ff5a9958b0b014922be318e9e1c8cc19c0011c8e2b46916a7687f96039e63`
  - evaluate: `0xf1efb585105e9e97ae75ac87e60fb6cf6e9ca547719eb30a916d1c21d65105eb`

V3 removes only that unsupported field check and retains target binding through
`total_commits == len(commits)` plus `commits[-1].sha == target_commit`.
