import hashlib
import json

import pytest


CONTRACT = "contracts/upgrade_diff_sentinel.py"
API_PATTERN = r"api\.github\.com/repos/example/protocol/compare/"
RAW_PATTERN = r"raw\.githubusercontent\.com/example/protocol/"
RELEASE_PATTERN = r"api\.github\.com/repos/example/protocol/releases/tags/"
CREATOR = "0x1111111111111111111111111111111111111111"
OTHER = "0x2222222222222222222222222222222222222222"
CREATOR_B = bytes.fromhex(CREATOR[2:])
OTHER_B = bytes.fromhex(OTHER[2:])
BASE = "a" * 40
TARGET = "b" * 40
MANIFEST_COMMIT = "c" * 40
PATH = "audit/upgrade.json"
TAG = "upgrade-v2"
SCOPE = "Only documentation and observability instrumentation may change."


def manifest_value(**changes):
    value = {
        "schema": "upgrade-diff-sentinel/v1",
        "repository": "example/protocol",
        "base_commit": BASE,
        "target_commit": TARGET,
        "changed_files": ["contracts/Vault.sol"],
        "declared_scope": ["documentation", "observability"],
        "forbidden_changes": ["authorization", "asset_flow", "fees", "storage_layout"],
    }
    value.update(changes)
    return value


def manifest_bytes(**changes):
    return json.dumps(manifest_value(**changes), sort_keys=True, separators=(",", ":")).encode()


def compare_value(**changes):
    value = {
        "status": "ahead",
        "base_commit": {"sha": BASE},
        "merge_base_commit": {"sha": BASE},
        "total_commits": 1,
        "commits": [{"sha": TARGET}],
        "files": [
            {"filename": "contracts/Vault.sol", "patch": "+emit UpgradeObserved();"},
        ],
    }
    value.update(changes)
    return value


def release_value(scope=SCOPE, **changes):
    manifest_digest = hashlib.sha256(manifest_bytes()).hexdigest()
    scope_digest = hashlib.sha256(scope.encode()).hexdigest()
    value = {
        "tag_name": TAG,
        "target_commitish": TARGET,
        "draft": False,
        "prerelease": False,
        "body": "\n".join([
            "upgrade_repository: example/protocol",
            f"upgrade_base_commit: {BASE}",
            f"upgrade_target_commit: {TARGET}",
            f"upgrade_manifest_commit: {MANIFEST_COMMIT}",
            f"upgrade_manifest_sha256: {manifest_digest}",
            f"upgrade_scope_sha256: {scope_digest}",
        ]),
    }
    value.update(changes)
    return value


def deploy(direct_vm, direct_deploy):
    direct_vm.strict_mocks = True
    direct_vm.check_pickling = True
    with direct_vm.prank(CREATOR_B):
        return direct_deploy(CONTRACT)


def create(contract, direct_vm, **changes):
    raw = manifest_bytes()
    values = {
        "owner": "example",
        "repository": "protocol",
        "base_commit": BASE,
        "target_commit": TARGET,
        "manifest_commit": MANIFEST_COMMIT,
        "manifest_path": PATH,
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "release_tag": TAG,
        "approved_scope": SCOPE,
    }
    values.update(changes)
    with direct_vm.prank(CREATOR_B):
        return contract.create_assessment(**values)


def mocks(direct_vm, compare=None, manifest=None, release=None, statuses=(200, 200, 200), model=None):
    direct_vm.mock_web(API_PATTERN, {"method": "GET", "status": statuses[0], "body": json.dumps(compare if compare is not None else compare_value())})
    direct_vm.mock_web(RAW_PATTERN, {"method": "GET", "status": statuses[1], "body": manifest if manifest is not None else manifest_bytes()})
    direct_vm.mock_web(RELEASE_PATTERN, {"method": "GET", "status": statuses[2], "body": json.dumps(release if release is not None else release_value())})
    direct_vm.mock_llm("UPGRADE_DIFF_SENTINEL_CLASSIFIER_V1", model or {
        "authorization_risk": "NO", "asset_flow_risk": "NO", "fee_risk": "NO",
        "storage_risk": "NO", "scope_alignment": "MATCH",
    })


def evaluate(contract, direct_vm, **kwargs):
    mocks(direct_vm, **kwargs)
    with direct_vm.prank(CREATOR_B):
        contract.evaluate_upgrade(0)


def test_happy_path_is_compatible_and_append_only(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_vm)
    evaluate(contract, direct_vm)
    record = contract.get_assessment(0)
    attempt = contract.get_attempt(0, 1)
    assert record.state == "COMPATIBLE"
    assert record.reason_code == "WITHIN_APPROVED_SCOPE"
    assert record.approved_scope_sha256 == hashlib.sha256(SCOPE.encode()).hexdigest()
    assert record.final_evidence_digest == attempt.evidence_digest
    assert contract.get_config()["compatible_count"] == 1
    assert contract.get_config()["version"] == "UPGRADE_DIFF_SENTINEL_V3"


@pytest.mark.parametrize("field,value,error", [
    ("owner", "bad/name", "INVALID_OWNER"),
    ("base_commit", "main", "INVALID_BASE_COMMIT"),
    ("target_commit", BASE, "IDENTICAL_COMMITS"),
    ("manifest_commit", TARGET, "MANIFEST_COMMIT_NOT_DISTINCT"),
    ("manifest_path", "../audit.json", "INVALID_MANIFEST_PATH"),
    ("manifest_sha256", "A" * 64, "INVALID_MANIFEST_DIGEST"),
    ("approved_scope", "too short", "INVALID_APPROVED_SCOPE"),
])
def test_invalid_create_is_atomic(direct_vm, direct_deploy, field, value, error):
    contract = deploy(direct_vm, direct_deploy)
    with direct_vm.expect_revert(error):
        create(contract, direct_vm, **{field: value})
    assert contract.get_config()["assessment_count"] == 0


def test_replay_rejected(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_vm)
    with direct_vm.expect_revert("ASSESSMENT_REPLAY"):
        create(contract, direct_vm)
    assert contract.get_config()["assessment_count"] == 1


@pytest.mark.parametrize("field,reason", [
    ("authorization_risk", "AUTHORIZATION_CHANGE"),
    ("asset_flow_risk", "ASSET_FLOW_CHANGE"),
    ("fee_risk", "FEE_CHANGE"),
    ("storage_risk", "STORAGE_RISK"),
])
def test_each_forbidden_semantic_change_fails_closed(direct_vm, direct_deploy, field, reason):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_vm)
    model = {"authorization_risk": "NO", "asset_flow_risk": "NO", "fee_risk": "NO", "storage_risk": "NO", "scope_alignment": "MATCH"}
    model[field] = "YES"
    evaluate(contract, direct_vm, model=model)
    assert contract.get_assessment(0).state == "INCOMPATIBLE"
    assert contract.get_assessment(0).reason_code == reason


@pytest.mark.parametrize("alignment,state,reason", [
    ("MISMATCH", "INCOMPATIBLE", "OUTSIDE_APPROVED_SCOPE"),
    ("UNCLEAR", "REVIEW_REQUIRED", "SEMANTIC_RESULT_UNCLEAR"),
])
def test_scope_results_are_closed(direct_vm, direct_deploy, alignment, state, reason):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_vm)
    model = {"authorization_risk": "NO", "asset_flow_risk": "NO", "fee_risk": "NO", "storage_risk": "NO", "scope_alignment": alignment}
    evaluate(contract, direct_vm, model=model)
    assert contract.get_assessment(0).state == state
    assert contract.get_assessment(0).reason_code == reason


@pytest.mark.parametrize("change", [
    {"status": "diverged"},
    {"base_commit": {"sha": TARGET}},
    {"total_commits": 101},
    {"total_commits": 2},
    {"commits": [{"sha": BASE}]},
])
def test_compare_identity_and_completeness_are_bound(direct_vm, direct_deploy, change):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_vm)
    evaluate(contract, direct_vm, compare=compare_value(**change))
    assert contract.get_assessment(0).reason_code == "COMPARE_BINDING_FAILED"


def test_manifest_digest_mismatch(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_vm)
    evaluate(contract, direct_vm, manifest=manifest_bytes(declared_scope=["altered"]))
    assert contract.get_assessment(0).reason_code == "MANIFEST_BINDING_FAILED"


def test_manifest_file_coverage_must_be_exact(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_vm)
    compare = compare_value(files=[{"filename": "docs/extra.md", "patch": "+extra"}])
    evaluate(contract, direct_vm, compare=compare)
    assert contract.get_assessment(0).reason_code == "FILE_COVERAGE_FAILED"


@pytest.mark.parametrize("change", [
    {"target_commitish": BASE}, {"draft": True}, {"prerelease": True},
    {"body": "upgrade_repository: example/protocol"},
])
def test_release_approval_binding(direct_vm, direct_deploy, change):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_vm)
    evaluate(contract, direct_vm, release=release_value(**change))
    assert contract.get_assessment(0).reason_code == "APPROVAL_BINDING_FAILED"


def test_scope_cannot_be_changed_without_release_approval(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    changed = "Any authorization and asset-flow changes are approved by the contributor."
    create(contract, direct_vm, approved_scope=changed)
    evaluate(contract, direct_vm, release=release_value())
    assert contract.get_assessment(0).reason_code == "APPROVAL_BINDING_FAILED"


@pytest.mark.parametrize("statuses", [(503, 200, 200), (200, 429, 200), (200, 200, 503), (404, 200, 200)])
def test_source_failures_are_retryable_and_do_not_finalize(direct_vm, direct_deploy, statuses):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_vm)
    evaluate(contract, direct_vm, statuses=statuses)
    record = contract.get_assessment(0)
    assert record.state == "REVIEW_REQUIRED"
    assert record.final_evidence_digest == ""


def test_retry_appends_attempt_then_finalizes(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_vm)
    evaluate(contract, direct_vm, statuses=(503, 200, 200))
    direct_vm.clear_mocks()
    mocks(direct_vm)
    with direct_vm.prank(CREATOR_B):
        contract.retry_assessment(0)
    assert contract.get_attempt(0, 1).source_status == "UNAVAILABLE"
    assert contract.get_attempt(0, 2).source_status == "VERIFIED"
    assert contract.get_assessment(0).state == "COMPATIBLE"


def test_wrong_caller_and_terminal_retry_preserve_state(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_vm)
    mocks(direct_vm)
    with direct_vm.prank(OTHER_B), direct_vm.expect_revert("CREATOR_ONLY"):
        contract.evaluate_upgrade(0)
    assert contract.get_assessment(0).attempt_count == 0
    evaluate(contract, direct_vm)
    with direct_vm.prank(CREATOR_B), direct_vm.expect_revert("ASSESSMENT_TERMINAL"):
        contract.retry_assessment(0)
    assert contract.get_assessment(0).attempt_count == 1


def test_malformed_model_is_review_required(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_vm)
    evaluate(contract, direct_vm, model={"decision": "approve"})
    assert contract.get_assessment(0).state == "REVIEW_REQUIRED"


def test_binary_or_unavailable_patch_is_review_required(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_vm)
    compare = compare_value(files=[{"filename": PATH}, {"filename": "contracts/Vault.sol", "patch": "+x"}])
    evaluate(contract, direct_vm, compare=compare)
    assert contract.get_assessment(0).state == "REVIEW_REQUIRED"


@pytest.mark.parametrize("compare,manifest", [
    (compare_value(files=[{"filename": "contracts/Vault.sol", "patch": "+x"}, {"filename": "contracts/Vault.sol", "patch": "+y"}]), None),
    (compare_value(files=[{"filename": "contracts/Vault.sol", "patch": "+" + "x" * 33000}]), None),
    (None, b"not-json"),
])
def test_malformed_or_oversized_canonical_data_never_passes(direct_vm, direct_deploy, compare, manifest):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_vm)
    evaluate(contract, direct_vm, compare=compare, manifest=manifest)
    assert contract.get_assessment(0).state == "REVIEW_REQUIRED"
    assert contract.get_assessment(0).final_evidence_digest == ""


def test_retry_cap_is_enforced_without_overwriting_attempts(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_vm)
    evaluate(contract, direct_vm, statuses=(503, 200, 200))
    for expected_attempt in (2, 3):
        direct_vm.clear_mocks()
        mocks(direct_vm, statuses=(503, 200, 200))
        with direct_vm.prank(CREATOR_B):
            contract.retry_assessment(0)
        assert contract.get_attempt(0, expected_attempt).source_status == "UNAVAILABLE"
    with direct_vm.prank(CREATOR_B), direct_vm.expect_revert("ATTEMPT_LIMIT_REACHED"):
        contract.retry_assessment(0)
    assert contract.get_assessment(0).attempt_count == 3


def test_validator_refetch_rejects_changed_evidence(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_vm)
    mocks(direct_vm)
    with direct_vm.prank(CREATOR_B):
        contract.evaluate_upgrade(0)
    # Direct Mode captures the validator callback. Replace canonical evidence
    # before executing it to prove that the validator independently refetches.
    direct_vm.clear_mocks()
    mocks(direct_vm, manifest=b"changed")
    assert direct_vm.run_validator() is False
