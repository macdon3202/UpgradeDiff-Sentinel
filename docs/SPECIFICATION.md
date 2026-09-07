# UpgradeDiff Sentinel specification

## Boundary

V1 audits one public GitHub repository upgrade. It supports a compare range, a
JSON manifest stored at a distinct exact attestation commit and a published GitHub Release
whose body approves the exact base, target and manifest digest. It does not
compile source, execute upgrades, custody assets or claim bytecode equivalence.

## Actor and sealed input

The authenticated transaction sender creates and evaluates an assessment. It
seals GitHub owner/repository, 40-hex base, target and manifest commits,
manifest path and SHA-256, published release tag and a plain-language approved
scope. No URL is an input. The manifest commit must differ from base and target,
so its content can truthfully bind the already-known target SHA.

## Canonical manifest schema

```json
{
  "schema": "upgrade-diff-sentinel/v1",
  "repository": "owner/repository",
  "base_commit": "40 hex",
  "target_commit": "40 hex",
  "changed_files": ["contracts/Vault.sol"],
  "declared_scope": ["gas optimization"],
  "forbidden_changes": ["authorization", "asset_flow", "fees", "storage_layout"]
}
```

The Release body must contain exact line markers for repository, base commit,
target commit, manifest commit, manifest SHA-256 and approved-scope SHA-256. Validators compute
both digests from fetched bytes or sealed scope; submitter declarations are not
accepted as observations.

## AI boundary

AI sees only the sealed scope, canonical manifest and bounded GitHub patches. It
returns five closed enums: four risk fields (`YES`, `NO`, `UNCLEAR`) and scope
alignment (`MATCH`, `MISMATCH`, `UNCLEAR`). It cannot return the final verdict.

## State machine

`SEALED -> COMPATIBLE | INCOMPATIBLE | REVIEW_REQUIRED`

`REVIEW_REQUIRED -> COMPATIBLE | INCOMPATIBLE | REVIEW_REQUIRED`

## Invariants

1. Only assessment creator can evaluate or retry.
2. Base and target must differ and one exact tuple can be sealed only once.
3. Compare status must be `ahead`; base, merge-base and head must match; the
   complete commit list must fit one bounded page; and every changed file must
   appear exactly once in the manifest.
4. Manifest bytes fetched at the distinct manifest commit and all identity
   fields must match sealed inputs.
5. Published release must point to the target commit and bind the repository,
   commits, manifest bytes and approved scope through exact-line markers.
6. Any deterministic mismatch is `INCOMPATIBLE`; unavailable/malformed sources
   and semantic uncertainty are `REVIEW_REQUIRED`.
7. `COMPATIBLE` requires every risk field `NO` and scope alignment `MATCH`.
8. Attempts are append-only, capped at three and terminal states are immutable.
9. Validators independently refetch all sources and recompute evidence digest.

## Honest limitation

This source-level auditor does not prove deployed bytecode parity or storage
layout safety. Those remain explicit external release gates and must not be
claimed from a `COMPATIBLE` result.
