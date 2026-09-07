# UpgradeDiff Sentinel

UpgradeDiff Sentinel is a GenLayer Intelligent Contract that checks whether a
GitHub protocol upgrade remains within a scope approved in a published GitHub
Release. The submitter seals repository identifiers, exact base/target commits,
a commit-pinned manifest digest and release tag. Validators independently fetch
GitHub's compare API, the raw manifest and the release record.

Deterministic code verifies repository identity, commit ancestry, changed-file
coverage, exact manifest digest and approval markers. A bounded model classifies
authorization, asset-flow, fee and storage risks plus declared-scope alignment.
The contract—not the model—derives the final state.

No arbitrary evidence URLs, custody, admin override or caller-supplied verdict
exist. Attempts are append-only, replay is blocked and all uncertain or
unavailable evidence fails closed.

## Local gates

```powershell
cd 'G:\Genlayer 4\UpgradeDiffSentinel'
genvm-lint check contracts\upgrade_diff_sentinel.py
gltest -q
```
