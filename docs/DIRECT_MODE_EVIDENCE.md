# Direct Mode verification — 2026-09-07

## Frozen artifacts

- Contract: `contracts/upgrade_diff_sentinel.py`
- Version: `UPGRADE_DIFF_SENTINEL_V3`
- Contract SHA-256: `2c8d2e0ad793f8e3a683b02993c0282c1f60a28b36d38dbe1c2a710265732bf0`
- Test SHA-256: `077bd71aa13be706a3b20b8b3f995e6c57e38f0b7486cc620126b1485700200b`
- Constructor inputs: none

## Reproducible commands and outcome

```text
genvm-lint check contracts\upgrade_diff_sentinel.py
PASS: lint (3 checks), validation, 6 methods (3 view, 3 write)

gltest -q --disable-warnings
PASS: 40 passed in 2.45s
```

The 27 suppressed warnings are expected unused-mock warnings after an earlier
canonical fetch fails closed; they are not contract exceptions or failed tests.

## Coverage represented by this evidence

- Compatible path with authoritative readback and digest persistence.
- Four forbidden semantic risk classes and scope mismatch/uncertainty.
- Compare base, merge-base, head, completeness and ancestry bindings.
- Exact manifest byte digest, changed-file coverage and release approval.
- Approved-scope digest binding to an exact GitHub Release marker.
- HTTP failure, malformed source/model, absent/binary and oversized patches.
- Creator authorization, replay resistance, terminal immutability and retry cap.
- Independent validator refetch with changed-evidence rejection.
- Distinct manifest-attestation commit preventing target-SHA self-reference.

## Evidence boundary

This is local GenLayer Direct Mode evidence. It is not a Studionet deployment,
live consensus receipt or production GitHub assessment. `source-manifest.json`
therefore intentionally keeps `deployment` null and `live_evidence` empty.
