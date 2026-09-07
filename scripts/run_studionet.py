"""Run UpgradeDiff Sentinel Studionet checks without exposing wallet keys."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet


RPC = "https://studio.genlayer.com/api"
EXPLORER = "https://explorer-studio.genlayer.com"
MAX_POLLS = 180


def load_wallets() -> None:
    path = Path(__file__).resolve().parents[2] / "secrets" / "genlayer-test-wallets.env"
    for raw in path.read_text(encoding="utf-8").splitlines():
        if "=" in raw and not raw.lstrip().startswith("#"):
            key, value = raw.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'\"").strip("<>"))


def plain(value):
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def read(client, address, account, method, args):
    return plain(client.read_contract(address=address, function_name=method, args=args, account=account))


def signals(info: dict) -> tuple[str, str, str]:
    status = str(info.get("status_name") or info.get("status") or "UNKNOWN").upper()
    consensus = str(info.get("result_name") or info.get("consensus_result_name") or info.get("consensus_result") or "UNKNOWN").upper()
    executions = []
    data = info.get("consensus_data")
    if isinstance(data, dict):
        receipts = data.get("leader_receipt") or data.get("leaderReceipt") or []
        if isinstance(receipts, dict):
            receipts = [receipts]
        for receipt in receipts if isinstance(receipts, list) else []:
            if isinstance(receipt, dict) and receipt.get("execution_result") is not None:
                executions.append(str(receipt["execution_result"]).upper())
    execution = "ERROR" if any("ERROR" in item or "FAIL" in item for item in executions) else "SUCCESS" if executions else str(info.get("execution_result") or "UNKNOWN").upper()
    return status, execution, consensus


def send(client, address, account, method, args, expect_error=False):
    tx = str(client.write_contract(address=address, function_name=method, account=account, args=args, value=0))
    for _ in range(MAX_POLLS):
        info = client.get_transaction(tx)
        status, execution, consensus = signals(info)
        if status == "FINALIZED":
            errored = "ERROR" in execution or "FAIL" in execution
            if errored != expect_error:
                raise RuntimeError(f"{method}: expected_error={expect_error}, execution={execution}")
            return {"method": method, "tx": tx, "status": status, "execution": execution, "consensus": consensus, "expected_error": expect_error, "explorer": f"{EXPLORER}/transactions/{tx}"}
        if status in {"FAILED", "REJECTED", "CANCELLED"}:
            raise RuntimeError(f"{method}: terminal status {status}")
        time.sleep(3)
    raise TimeoutError(f"{method}: transaction not terminal: {tx}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("address")
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--post-negative", action="store_true")
    args = parser.parse_args()
    load_wallets()
    wallet_a = create_account(os.environ["SERVICE_LEDGER_KEY_A"])
    wallet_b = create_account(os.environ["SERVICE_LEDGER_KEY_B"])
    client = create_client(chain=studionet, account=wallet_a, endpoint=RPC)
    config = read(client, args.address, wallet_a, "get_config", [])
    expected = {"version": "UPGRADE_DIFF_SENTINEL_V3", "github_api": "https://api.github.com", "github_raw": "https://raw.githubusercontent.com", "max_attempts": 3}
    if any(config.get(key) != value for key, value in expected.items()):
        raise RuntimeError(f"unexpected deployment config: {config}")
    evidence = {"network": "studionet", "contract": args.address, "explorer": f"{EXPLORER}/address/{args.address}", "config": config, "transactions": [], "readbacks": {}}
    if args.fixture and not args.post_negative:
        fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
        assessment_id = int(config["assessment_count"])
        create_args = [fixture[key] for key in ("owner", "repository", "base_commit", "target_commit", "manifest_commit", "manifest_path", "manifest_sha256", "release_tag", "approved_scope")]
        evidence["transactions"].append(send(client, args.address, wallet_a, "create_assessment", create_args))
        sealed = read(client, args.address, wallet_a, "get_assessment", [assessment_id])
        evidence["readbacks"]["sealed"] = sealed
        before_negative = read(client, args.address, wallet_a, "get_config", [])
        evidence["transactions"].append(send(client, args.address, wallet_b, "evaluate_upgrade", [assessment_id], True))
        if read(client, args.address, wallet_a, "get_config", []) != before_negative or read(client, args.address, wallet_a, "get_assessment", [assessment_id]) != sealed:
            raise AssertionError("wrong-caller failure mutated state")
        evidence["transactions"].append(send(client, args.address, wallet_a, "evaluate_upgrade", [assessment_id]))
        evidence["readbacks"]["final"] = read(client, args.address, wallet_a, "get_assessment", [assessment_id])
        evidence["readbacks"]["attempt_1"] = read(client, args.address, wallet_a, "get_attempt", [assessment_id, 1])
    elif args.fixture and args.post_negative:
        fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
        create_args = [fixture[key] for key in ("owner", "repository", "base_commit", "target_commit", "manifest_commit", "manifest_path", "manifest_sha256", "release_tag", "approved_scope")]
        before_config = read(client, args.address, wallet_a, "get_config", [])
        assessment_id = int(before_config["assessment_count"]) - 1
        before_record = read(client, args.address, wallet_a, "get_assessment", [assessment_id])
        evidence["transactions"].append(send(client, args.address, wallet_a, "create_assessment", create_args, True))
        evidence["transactions"].append(send(client, args.address, wallet_a, "retry_assessment", [assessment_id], True))
        after_config = read(client, args.address, wallet_a, "get_config", [])
        after_record = read(client, args.address, wallet_a, "get_assessment", [assessment_id])
        if after_config != before_config or after_record != before_record:
            raise AssertionError("post-terminal negative calls mutated state")
        evidence["readbacks"] = {"before_config": before_config, "after_config": after_config, "terminal_record": after_record}
    filename = "studionet-negative-calls.json" if args.post_negative else "studionet-lifecycle.json"
    out = Path(__file__).resolve().parents[1] / "docs" / filename
    out.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
