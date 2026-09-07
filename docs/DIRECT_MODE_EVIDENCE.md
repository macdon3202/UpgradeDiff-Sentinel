# Direct Mode verification — 2026-09-07

## Frozen artifacts

- Contract: `contracts/upgrade_diff_sentinel.py`
- Version: `UPGRADE_DIFF_SENTINEL_V2`
- Contract SHA-256: `6631c3dc2bb77d6ae03ea02ca6f454639dcdc4630feee2ecd80dbdbc82951c96`
- Test SHA-256: `2ef1cf48eb33c4ba1b61466ec1c8d16aef1cb757d446bbd764f06bc5c2d782d9`
- Constructor inputs: none

## Reproducible commands and outcome

```text
genvm-lint check contracts\upgrade_diff_sentinel.py
PASS: lint (3 checks), validation, 6 methods (3 view, 3 write)

gltest -q --disable-warnings
PASS: 40 passed in 2.86s
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
