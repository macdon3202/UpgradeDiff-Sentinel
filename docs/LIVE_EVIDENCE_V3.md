# V3 Studionet lifecycle evidence

Contract: `0x455f601Cf9cb73c08df9c4DA6DB6f469e8143306`

`get_config` authoritatively returned `UPGRADE_DIFF_SENTINEL_V3` and the fixed
canonical origins. The current SDK does not expose deployed source bytes, so
exact Explorer source-byte parity remains an explicit limitation.

Canonical fixture: `macdon3202/upgrade-diff-sentinel-fixture`, published
Release `upgrade-v2`.

## Successful lifecycle

- `create_assessment`: FINALIZED, execution SUCCESS, MAJORITY_AGREE
  - tx `0x8baabf1d46e6645e9b1edc0ae4323ebf94e83490609b050b44d00f29dc26f8f9`
- Wrong-wallet `evaluate_upgrade`: FINALIZED, expected execution ERROR,
  MAJORITY_AGREE; sealed state and counters unchanged
  - tx `0x10da9d369634a56771ce2126d33a37521e8c5ff57f61eedd69925206636a5b18`
- Creator `evaluate_upgrade`: FINALIZED, execution SUCCESS, MAJORITY_AGREE
  - tx `0x3664848115f124e29a0c526b22fd4a1fde25b3700afd0af46728503b392a6250`

Authoritative readback: `COMPATIBLE / WITHIN_APPROVED_SCOPE`, attempt count 1,
all four risk fields `NO`, all deterministic bindings and scope alignment
`MATCH`, evidence digest
`99bf91824a13beb5e2f378db8d37b7462bb0ab05dd6f536af976a38783f83ae4`.

## Post-terminal negative calls

- Duplicate `create_assessment`: FINALIZED, expected ERROR, MAJORITY_AGREE
  - tx `0xea25c6b61f6d35e3a4704931c8a923a5288d0a08b467db54be13dc30fe0e6f44`
- Terminal `retry_assessment`: FINALIZED, expected ERROR, MAJORITY_AGREE
  - tx `0x26ff72205850575a3dc9f63537372c1f523e49e25968c83fe162eef9eeeb05a3`

Before/after config is identical: one assessment, one compatible verdict, zero
incompatible verdicts. The terminal record and final digest are unchanged.

Machine-readable transaction data and full readbacks are retained in
`studionet-lifecycle.json` and `studionet-negative-calls.json`.
