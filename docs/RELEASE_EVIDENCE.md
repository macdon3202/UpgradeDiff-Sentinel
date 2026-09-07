# Release checklist

- [x] GenVM lint and validation pass.
- [x] Direct Mode happy, failure and adversarial matrix pass.
- [x] Source SHA-256 frozen before deployment.
- [ ] Explorer source-byte export parity (not exposed by current SDK readback).
- [x] `get_config` returns the expected version and canonical origins.
- [x] One compatible live path is independently read back.
- [x] Negative live calls prove no mutation.

An incompatible live assessment is not required for this release because all
deterministic and semantic incompatible branches are covered in Direct Mode.
The V2 live compare-binding failure is preserved as superseded evidence, not
misrepresented as a V3 product path.

Direct fixtures must never be represented as live GitHub or Studionet evidence.
V3 live evidence is stored separately in `studionet-lifecycle.json` and
`studionet-negative-calls.json`.
