import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / "contracts" / "upgrade_diff_sentinel.py"
record = {
    "contract": "UpgradeDiffSentinel",
    "version": "UPGRADE_DIFF_SENTINEL_V3",
    "source": "contracts/upgrade_diff_sentinel.py",
    "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "constructor": [],
    "deployment": None,
    "live_evidence": [],
}
(root / "docs" / "source-manifest.json").write_text(
    json.dumps(record, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(record, indent=2))
