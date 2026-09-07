# Direct Mode verification — 2026-09-07

## Frozen artifacts

- Contract: `contracts/upgrade_diff_sentinel.py`
- Version: `UPGRADE_DIFF_SENTINEL_V1`
- Contract SHA-256: `e6b4f35608236221f101ee208bbde35f448bae7e33b4fadaf8e91d3f1f924fde`
- Test SHA-256: `64f958b52f8a923c09c3f8194098e2c1fa86ded93c1629eb3ad655a42ca79991`
- Constructor inputs: none

## Reproducible commands and outcome

```text
genvm-lint check contracts\upgrade_diff_sentinel.py
PASS: lint (3 checks), validation, 6 methods (3 view, 3 write)

gltest -q --disable-warnings
PASS: 39 passed in 2.47s
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

## Evidence boundary

This is local GenLayer Direct Mode evidence. It is not a Studionet deployment,
live consensus receipt or production GitHub assessment. `source-manifest.json`
therefore intentionally keeps `deployment` null and `live_evidence` empty.
