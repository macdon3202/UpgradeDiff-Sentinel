# Release checklist

- [ ] GenVM lint and validation pass.
- [ ] Direct Mode happy, failure and adversarial matrix pass.
- [ ] Source SHA-256 frozen before deployment.
- [ ] Deployment source bytes exactly match frozen source.
- [ ] `get_config` returns the expected version and canonical origins.
- [ ] One compatible and one incompatible live path are independently read back.
- [ ] Negative live calls prove no mutation.

Direct fixtures must never be represented as live GitHub or Studionet evidence.
