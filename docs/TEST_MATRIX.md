# Test matrix

| Class | Coverage |
|---|---|
| Happy | compatible gas-only diff |
| Semantic | authorization, asset flow, fee, storage and scope mismatch |
| Canonical | repository, base/target, manifest digest/schema and release markers |
| Diff integrity | ancestry, duplicate/missing/extra paths, truncated/oversized patch |
| Failure | HTTP 429/5xx, 4xx, malformed JSON, malformed model output |
| State | creator authority, tuple replay, terminal retry, max attempts |
| Consensus | validator refetch and changed-source rejection |

Live Studionet evidence must additionally include source parity, finalized
execution/consensus receipts and authoritative assessment/attempt readback.
