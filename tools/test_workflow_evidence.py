"""WO-U04 / WP-03 — reuse verification only for equivalent declared inputs (spec WS-08,
WS-15 §17.1; verification WT-11, WT-22).

A passed check receipt is reusable only when the current input manifest proves the same
declared inputs: every material source/test/config/lock/checker/environment/base/policy
or membership change invalidates it, unrelated documents and classified logs do not, and
failed, corrupt or unreadable receipts never pass. Path identity is byte-exact, symlinks
that escape the repository and unsupported paths refuse reuse, and explicit task subjects
are never hidden by an artifact classification.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import unicodedata
from dataclasses import replace
from pathlib import Path

import pytest

from tools.workflow_evidence import (
    AcceptedInstall,
    Behaved,
    Behaves,
    Checker,
    CheckReceipt,
    CheckRequest,
    EvidenceError,
    GitTree,
    Index,
    InfrastructureFailed,
    InputManifest,
    InstalledCandidate,
    InstalledRun,
    ReceiptDefect,
    Reference,
    Refused,
    Refuses,
    ScenarioObservation,
    Threshold,
    WorkingTree,
    accepted_build_install,
    admit_scenario,
    bind_acceptance,
    build_manifest,
    check_receipt,
    equivalence_record,
    install_equivalence_record,
    install_reuse,
    judge_scenario,
    load_receipt,
    observe_install,
    parse_equivalence,
    parse_receipt,
    parse_scenario_contract,
    reuse_result,
)
from tools.workflow_policy import WorkflowPolicy, parse_policy

TRACKED_POLICY = Path(__file__).resolve().parents[1] / ".harness" / "workflow-policy.json"
UNIT = "arhugula-harness-trial-193.7x7.9tj"
REPOSITORY = "thestoryportal/arhugula-harness"


def _policy(artifact_roots: dict | None = None) -> WorkflowPolicy:
    doc = {
        "schema_version": 1,
        "policy_id": "arhugula-trial-v1",
        "policy_version": 1,
        "lit_project": "arhugula",
        "trial_root": "arhugula-harness-trial-193",
        "eligible_units": [],
        "boundary_rules": {},
        "check_inputs": {},
        "artifact_roots": artifact_roots
        or {
            "code_roots": ["ops", "tests", "tools"],
            "artifact_roots": [{"root": "evidence/logs", "purpose": "generated pytest logs"}],
        },
        "review_rules": {},
        "compatibility": {"phase_record_versions": [1]},
    }
    return parse_policy(json.dumps(doc).encode())


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.invalid")
    _git(root, "config", "user.name", "t")
    _write(root, "ops/core.py", "VALUE = 1\n")
    _write(root, "tests/test_core.py", "def test_value():\n    assert True\n")
    _write(root, "tests/conftest.py", "")
    _write(root, "pyproject.toml", "[tool.pytest.ini_options]\n")
    _write(root, "uv.lock", "version = 1\n")
    _write(root, "tools/checker.py", "print('check')\n")
    _write(root, "docs/notes.md", "notes\n")
    _write(root, ".gitignore", ".local/\n__pycache__/\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    return root


def _request(root: Path, **overrides: object) -> CheckRequest:
    fields: dict[str, object] = {
        "unit": UNIT,
        "repository": REPOSITORY,
        "scope": WorkingTree(),
        "policy": _policy(),
        "checker": Checker(
            name="pytest", version="8.4.1", argv=("python", "-m", "pytest", "tests", "-q")
        ),
        "domains": ("ops", "tests", "evidence"),
        "explicit": ("pyproject.toml", "uv.lock", "tools/checker.py"),
        "environment": {"python": "3.12.11", "uv": "0.8.0"},
        "material_base": None,
        "closure": "declared",
    }
    fields.update(overrides)
    return CheckRequest(**fields)  # type: ignore[arg-type]


def _passed_receipt(manifest: InputManifest, result: str = "passed") -> CheckReceipt:
    record = check_receipt(
        manifest,
        record_id="rcpt-1",
        producer={"tool": "pytest", "version": "8.4.1"},
        created_at="2026-10-23T23:30:00Z",
        result=result,  # type: ignore[arg-type]
        artifacts=[],
    )
    return parse_receipt(json.dumps(record).encode())


def _reuse(root: Path, prior: CheckReceipt, **overrides: object):
    return reuse_result(prior, build_manifest(root, _request(root, **overrides)))


def _snapshot(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file() and ".git" not in path.relative_to(root).parts
    }


def test_unchanged_inputs_reuse_the_passed_result(repo: Path) -> None:
    prior = _passed_receipt(build_manifest(repo, _request(repo)))

    decision = _reuse(repo, prior)

    assert decision.reusable is True
    assert decision.reasons == ()
    assert decision.prior_record == "rcpt-1"
    assert decision.key == prior.manifest.key


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        ("source", "files_changed"),
        ("test", "files_changed"),
        ("config", "files_changed"),
        ("lock", "files_changed"),
        ("checker_bytes", "files_changed"),
        ("checker_version", "checker_changed"),
        ("checker_argv", "checker_changed"),
        ("environment", "environment_changed"),
        ("base", "material_base_changed"),
        ("membership", "membership_changed"),
        ("domains", "domains_changed"),
        ("mode", "files_changed"),
        ("delete", "files_changed"),
        ("rename", "membership_changed"),
        ("policy", "policy_changed"),
    ],
)
def test_reuse_invalidates_every_material_input(repo: Path, mutation: str, reason: str) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    prior = _passed_receipt(build_manifest(repo, _request(repo, material_base=base)))
    overrides: dict[str, object] = {"material_base": base}
    if mutation == "source":
        _write(repo, "ops/core.py", "VALUE = 2\n")
    elif mutation == "test":
        _write(repo, "tests/test_core.py", "def test_value():\n    assert False\n")
    elif mutation == "config":
        _write(repo, "pyproject.toml", "[tool.pytest.ini_options]\naddopts = '-x'\n")
    elif mutation == "lock":
        _write(repo, "uv.lock", "version = 2\n")
    elif mutation == "checker_bytes":
        _write(repo, "tools/checker.py", "print('changed')\n")
    elif mutation == "checker_version":
        overrides["checker"] = replace(_request(repo).checker, version="8.4.2")
    elif mutation == "checker_argv":
        overrides["checker"] = replace(_request(repo).checker, argv=("python", "-m", "pytest"))
    elif mutation == "environment":
        overrides["environment"] = {"python": "3.12.12", "uv": "0.8.0"}
    elif mutation == "base":
        _write(repo, "docs/notes.md", "moved base\n")
        _git(repo, "commit", "-q", "-am", "next")
        overrides["material_base"] = _git(repo, "rev-parse", "HEAD")
    elif mutation == "membership":
        _write(repo, "ops/new_module.py", "")  # genuine untracked source
    elif mutation == "domains":
        overrides["domains"] = ("ops",)
    elif mutation == "mode":
        (repo / "ops/core.py").chmod(0o755)
    elif mutation == "delete":
        (repo / "ops/core.py").unlink()
    elif mutation == "rename":
        (repo / "ops/core.py").rename(repo / "ops/renamed.py")
    elif mutation == "policy":
        overrides["policy"] = _policy(
            {"code_roots": ["ops", "tests", "tools", "harness-core"], "artifact_roots": []}
        )

    decision = _reuse(repo, prior, **overrides)

    assert decision.reusable is False
    assert reason in decision.reasons


def test_unrelated_documents_and_classified_logs_preserve_results(repo: Path) -> None:
    prior = _passed_receipt(build_manifest(repo, _request(repo)))
    _write(repo, "docs/notes.md", "rewritten notes\n")
    _write(repo, "README.md", "new readme\n")
    _write(repo, "evidence/logs/run.log", "generated output\n")

    decision = _reuse(repo, prior)

    assert decision.reusable is True


def test_untracked_source_overrides_artifact_domain(repo: Path) -> None:
    prior = _passed_receipt(build_manifest(repo, _request(repo)))
    # No artifact root may overlap a code root, whether it claims the whole root or a
    # directory nested inside it: the overlap is ambiguous and holds.
    for root in ("tests", "tests/logs-out"):
        overlapping = _policy(
            {
                "code_roots": ["ops", "tests", "tools"],
                "artifact_roots": [{"root": root, "purpose": "claims code as artifacts"}],
            }
        )
        ambiguous = _reuse(repo, prior, policy=overlapping)
        assert ambiguous.reusable is False
        assert "classification_ambiguous" in ambiguous.reasons

    # Genuine untracked tests/ source is visible and changes membership.
    _write(repo, "tests/test_new.py", "def test_new():\n    assert True\n")
    untracked = _reuse(repo, prior)
    assert untracked.reusable is False
    assert "membership_changed" in untracked.reasons

    # A historical ignored `.local` driver named as the task subject is an input even
    # though discovery would never find it, and its bytes invalidate the result.
    _write(repo, ".local/driver.py", "print('driver v1')\n")
    explicit = ("pyproject.toml", "uv.lock", "tools/checker.py", ".local/driver.py")
    with_driver = _passed_receipt(build_manifest(repo, _request(repo, explicit=explicit)))
    assert ".local/driver.py" in {entry.path for entry in with_driver.manifest.files}
    _write(repo, ".local/driver.py", "print('driver v2')\n")
    assert _reuse(repo, with_driver, explicit=explicit).reusable is False

    # An explicit subject inside a classified artifact root stays an input.
    _write(repo, "evidence/logs/subject.py", "x = 1\n")
    subject = ("pyproject.toml", "uv.lock", "tools/checker.py", "evidence/logs/subject.py")
    manifest = build_manifest(repo, _request(repo, explicit=subject))
    assert "evidence/logs/subject.py" in {entry.path for entry in manifest.files}


def test_path_identity_does_not_alias_source(repo: Path) -> None:
    nfc = unicodedata.normalize("NFC", "ops/café.py")
    nfd = unicodedata.normalize("NFD", "ops/café.py")
    _write(repo, nfc, "same = 1\n")
    prior = _passed_receipt(build_manifest(repo, _request(repo)))
    os.rename(repo / nfc, repo / nfd)
    renamed = _reuse(repo, prior)
    assert renamed.reusable is False
    assert "membership_changed" in renamed.reasons

    os.rename(repo / nfd, repo / nfc)
    assert _reuse(repo, prior).reusable is True
    (repo / nfc).rename(repo / "ops/CAFÉ.py")
    assert _reuse(repo, prior).reusable is False

    # A symlink escaping the repository refuses reuse instead of being traversed.
    (repo / "ops/CAFÉ.py").rename(repo / nfc)
    outside = repo.parent / "outside.py"
    outside.write_text("secret = 1\n", encoding="utf-8")
    (repo / "ops/escape.py").symlink_to(outside)
    escaped = build_manifest(repo, _request(repo))
    assert "symlink_escape" in {refusal.code for refusal in escaped.refusals}
    assert reuse_result(prior, escaped).reusable is False

    # A symlink inside the repository is identified by its target, not followed.
    (repo / "ops/escape.py").unlink()
    (repo / "ops/alias.py").symlink_to("core.py")
    internal = build_manifest(repo, _request(repo))
    alias = next(entry for entry in internal.files if entry.path == "ops/alias.py")
    assert (alias.kind, alias.mode) == ("symlink", "120000")
    assert internal.refusals == ()


def test_unsupported_path_bytes_refuse_reuse(repo: Path) -> None:
    prior = _passed_receipt(build_manifest(repo, _request(repo)))
    os.close(os.open(os.fsencode(repo / "ops") + b"/bad\xff.py", os.O_CREAT | os.O_WRONLY))

    decision = _reuse(repo, prior)

    assert decision.reusable is False
    assert "unsupported_path" in decision.reasons


def test_unknown_dependency_closure_requires_execution(repo: Path) -> None:
    prior = _passed_receipt(build_manifest(repo, _request(repo)))

    decision = _reuse(repo, prior, closure="unknown")

    assert decision.reusable is False
    assert "dependency_closure_unknown" in decision.reasons


@pytest.mark.parametrize("result", ["failed", "held", "error"])
def test_non_passing_prior_result_is_never_reused(repo: Path, result: str) -> None:
    prior = _passed_receipt(build_manifest(repo, _request(repo)), result=result)

    decision = _reuse(repo, prior)

    assert decision.reusable is False
    assert "prior_not_passed" in decision.reasons


def test_corrupt_or_unreadable_receipt_is_never_reused(repo: Path) -> None:
    manifest = build_manifest(repo, _request(repo))
    record = check_receipt(
        manifest,
        record_id="rcpt-1",
        producer={"tool": "pytest", "version": "8.4.1"},
        created_at="2026-10-23T23:30:00Z",
        result="passed",
        artifacts=[],
    )
    tampered = json.loads(json.dumps(record))
    tampered["inputs"]["manifest"]["files"][0]["sha256"] = "0" * 64
    duplicate_key = json.dumps(record)[:-1] + ', "result": "passed"}'
    old_fingerprint = dict(record, inputs={"worktree_fingerprint": "0123456789abcdef"})
    future_major = dict(record, schema_version=2)
    float_version = json.dumps(dict(record, producer={"tool": "pytest", "elapsed": 1.5}))
    bad_scope = json.loads(json.dumps(record))
    bad_scope["inputs"]["manifest"]["scope"] = "somewhere"
    other_unit = dict(record, unit_id="wrong")
    other_base = dict(record, subject=dict(record["subject"], base="0" * 40))

    for raw in (
        json.dumps(tampered).encode(),
        duplicate_key.encode(),
        json.dumps(old_fingerprint).encode(),
        json.dumps(future_major).encode(),
        float_version.encode(),
        json.dumps(bad_scope).encode(),
        json.dumps(other_unit).encode(),
        json.dumps(other_base).encode(),
        b"\x00not json",
    ):
        prior = load_receipt(raw)
        assert isinstance(prior, ReceiptDefect)
        decision = reuse_result(prior, manifest)
        assert decision.reusable is False
        assert decision.reasons == ("prior_unreadable",)
    with pytest.raises(EvidenceError):
        parse_receipt(json.dumps(tampered).encode())


def test_staged_worktree_divergence_refuses_false_reuse(repo: Path) -> None:
    _write(repo, "ops/core.py", "VALUE = 'staged'\n")
    _git(repo, "add", "ops/core.py")
    _write(repo, "ops/core.py", "VALUE = 'worktree'\n")
    worktree = build_manifest(repo, _request(repo))
    staged = build_manifest(repo, _request(repo, scope=Index()))
    assert reuse_result(_passed_receipt(worktree), staged).reusable is False

    # Once the index matches the verified worktree bytes, the identities are equivalent.
    _git(repo, "add", "ops/core.py")
    restaged = build_manifest(repo, _request(repo, scope=Index()))
    assert reuse_result(_passed_receipt(worktree), restaged).reusable is True


def test_committed_tree_matches_clean_worktree_identity(repo: Path) -> None:
    head = _git(repo, "rev-parse", "HEAD")
    committed = build_manifest(repo, _request(repo, scope=GitTree(head)))
    worktree = build_manifest(repo, _request(repo))

    assert committed.head == head
    assert committed.key == worktree.key
    assert reuse_result(_passed_receipt(committed), worktree).reusable is True


def test_manifest_is_canonical_and_preserves_every_byte(repo: Path) -> None:
    _write(repo, "evidence/logs/run.log", "protected evidence\n")
    before = _snapshot(repo)

    first = build_manifest(repo, _request(repo))
    second = build_manifest(repo, _request(repo, domains=("evidence", "tests", "ops")))

    assert _snapshot(repo) == before
    paths = [entry.path.encode() for entry in first.files]
    assert paths == sorted(paths)
    assert "evidence/logs/run.log" not in {entry.path for entry in first.files}
    assert first.key == second.key


@pytest.mark.parametrize(
    "bad",
    [
        {"code_roots": ["ops"]},
        {"code_roots": ["../ops"], "artifact_roots": []},
        {"code_roots": ["ops"], "artifact_roots": [{"root": "logs", "purpose": ""}]},
        {"code_roots": ["/abs"], "artifact_roots": []},
    ],
)
def test_malformed_classification_refuses_reuse(repo: Path, bad: dict[str, object]) -> None:
    manifest = build_manifest(repo, _request(repo, policy=_policy(bad)))

    assert "classification_invalid" in {refusal.code for refusal in manifest.refusals}


@pytest.mark.parametrize("path", ["../escape", "/abs", "", "a//b", "./a"])
def test_request_paths_are_repository_relative(repo: Path, path: str) -> None:
    with pytest.raises(EvidenceError):
        _request(repo, domains=(path,))


def test_tracked_policy_classification_is_usable(repo: Path) -> None:
    tracked = parse_policy(TRACKED_POLICY.read_bytes())

    manifest = build_manifest(repo, _request(repo, policy=tracked))

    assert manifest.refusals == ()
    assert manifest.policy_digest == tracked.digest


def test_non_file_entries_refuse_instead_of_aliasing(repo: Path) -> None:
    head = _git(repo, "rev-parse", "HEAD")
    _git(repo, "update-index", "--add", "--cacheinfo", f"160000,{head},ops/vendored")
    _git(repo, "commit", "-q", "-m", "gitlink")

    for scope in (GitTree("HEAD"), Index()):
        manifest = build_manifest(repo, _request(repo, scope=scope))
        assert "unsupported_entry" in {refusal.code for refusal in manifest.refusals}


def test_unmerged_index_has_no_staged_identity(repo: Path) -> None:
    _git(repo, "checkout", "-q", "-b", "other")
    _write(repo, "ops/core.py", "VALUE = 'other'\n")
    _git(repo, "commit", "-q", "-am", "other")
    _git(repo, "checkout", "-q", "main")
    _write(repo, "ops/core.py", "VALUE = 'main'\n")
    _git(repo, "commit", "-q", "-am", "main")
    merge = subprocess.run(["git", "merge", "other"], cwd=repo, capture_output=True, check=False)
    assert merge.returncode != 0

    manifest = build_manifest(repo, _request(repo, scope=Index()))

    assert "unsupported_entry" in {refusal.code for refusal in manifest.refusals}


def test_manifest_root_must_be_the_repository_top_level(repo: Path) -> None:
    with pytest.raises(EvidenceError):
        build_manifest(repo / "ops", _request(repo))


def test_receipt_from_an_incomplete_manifest_is_never_reused(repo: Path) -> None:
    incomplete = build_manifest(repo, _request(repo, closure="unknown"))
    prior = _passed_receipt(incomplete)

    decision = _reuse(repo, prior)

    assert decision.reusable is False
    assert decision.reasons == ("prior_incomplete",)


def test_explicit_input_through_a_symlinked_directory_refuses(repo: Path) -> None:
    outside = repo.parent / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("outside bytes\n", encoding="utf-8")
    (repo / "link").symlink_to("../outside")
    (repo / "alias").symlink_to("ops")

    for subject in ("link/secret.txt", "alias/core.py"):
        manifest = build_manifest(repo, _request(repo, explicit=(subject,)))
        assert subject not in {entry.path for entry in manifest.files}
        assert "symlink_traversal" in {refusal.code for refusal in manifest.refusals}


def _equivalence_bytes(prior: CheckReceipt, current: InputManifest, tmp: Path) -> bytes:
    record = equivalence_record(
        prior,
        current,
        record_id="equiv-1",
        producer={"tool": "workflow_evidence", "version": "1"},
        created_at="2026-10-23T23:45:00Z",
    )
    # The producer publishes the record durably; reuse consumes the bytes read back.
    published = tmp / "equivalence.json"
    published.write_text(json.dumps(record), encoding="utf-8")
    return published.read_bytes()


def test_cross_head_reuse_requires_a_durable_equivalence_receipt(
    repo: Path, tmp_path: Path
) -> None:
    prior = _passed_receipt(build_manifest(repo, _request(repo)))
    _write(repo, "docs/notes.md", "documentation only\n")
    _git(repo, "commit", "-q", "-am", "docs only")
    current = build_manifest(repo, _request(repo))
    assert current.head != prior.manifest.head
    assert current.key == prior.manifest.key

    without = reuse_result(prior, current)
    assert without.reusable is False
    assert without.reasons == ("equivalence_required",)

    equivalence = parse_equivalence(_equivalence_bytes(prior, current, tmp_path))
    bound = reuse_result(prior, current, equivalence)
    assert bound.reusable is True
    assert bound.equivalence == "equiv-1"

    # An equivalence for another head or another prior record binds nothing here.
    _write(repo, "docs/notes.md", "another docs-only commit\n")
    _git(repo, "commit", "-q", "-am", "docs again")
    later = build_manifest(repo, _request(repo))
    stale = reuse_result(prior, later, equivalence)
    assert stale.reusable is False
    assert stale.reasons == ("equivalence_mismatch",)


def test_equivalence_is_refused_for_different_inputs(repo: Path) -> None:
    prior = _passed_receipt(build_manifest(repo, _request(repo)))
    _write(repo, "ops/core.py", "VALUE = 3\n")
    _git(repo, "commit", "-q", "-am", "source change")

    with pytest.raises(EvidenceError):
        equivalence_record(
            prior,
            build_manifest(repo, _request(repo)),
            record_id="equiv-2",
            producer={"tool": "workflow_evidence", "version": "1"},
            created_at="2026-10-23T23:45:00Z",
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        (("policy_id",), "wrong"),
        (("policy_version",), 2),
        (("unit_id",), "wrong"),
        (("subject", "repository"), "wrong"),
        (("subject", "base"), "0" * 40),
    ],
)
def test_equivalence_whose_identity_contradicts_the_current_manifest_binds_nothing(
    repo: Path, tmp_path: Path, field: tuple[str, ...], value: object
) -> None:
    prior = _passed_receipt(build_manifest(repo, _request(repo)))
    _write(repo, "docs/notes.md", "documentation only\n")
    _git(repo, "commit", "-q", "-am", "docs only")
    current = build_manifest(repo, _request(repo))
    record = json.loads(_equivalence_bytes(prior, current, tmp_path))
    *parents, leaf = field
    target = record
    for name in parents:
        target = target[name]
    target[leaf] = value

    decision = reuse_result(prior, current, parse_equivalence(json.dumps(record).encode()))

    assert decision.reusable is False
    assert decision.reasons == ("equivalence_mismatch",)


def test_equivalence_whose_heads_disagree_is_refused_at_parse(repo: Path, tmp_path: Path) -> None:
    prior = _passed_receipt(build_manifest(repo, _request(repo)))
    _write(repo, "docs/notes.md", "documentation only\n")
    _git(repo, "commit", "-q", "-am", "docs only")
    record = json.loads(_equivalence_bytes(prior, build_manifest(repo, _request(repo)), tmp_path))
    record["inputs"]["current_head"] = "0" * 40

    with pytest.raises(EvidenceError):
        parse_equivalence(json.dumps(record).encode())


# --- WO-U19: installed reuse and scenario contracts (WS-12, WS-13; WT-17, WT-19) ---------

ACCEPTED_RECORD = "sha256:" + "b" * 64
WHEEL = "distribution:harness_core-0.0.0-py3-none-any.whl"
ARTIFACT: dict[str, str | None] = {
    WHEEL: "a" * 64,
    "installed:harness_core": "version=0.0.0; editable=false; record=19 verified",
    "site_packages": "/exec/venv/lib/python3.12/site-packages",
    "origins": "339 harness modules in site-packages",
}
ENVIRONMENT: dict[str, str | None] = {"python": "/uv/cpython-3.12.14/bin/python3.12"}
DIFFERING = "version=0.0.0; editable=false; record=18 verified, 1 differ"
SOURCE_REF = {"uri": "file:///accepted/operating-targets-v1.md", "sha256": "d" * 64, "bytes": 10}


def _installed_request(root: Path) -> CheckRequest:
    # Installed inputs only: package source plus project/lock. `tools/` is a gate.
    return _request(
        root,
        scope=GitTree("HEAD"),
        checker=Checker(name="uv-build", version="0.12.21", argv=("uv", "build", "--all")),
        domains=("ops",),
        explicit=("pyproject.toml", "uv.lock"),
    )


def _candidate(
    root: Path,
    artifact: dict[str, str | None] | None = None,
    environment: dict[str, str | None] | None = None,
) -> InstalledCandidate:
    return InstalledCandidate(
        source=build_manifest(root, _installed_request(root)),
        artifact={**ARTIFACT, **(artifact or {})},
        environment={**ENVIRONMENT, **(environment or {})},
    )


def _accepted(root: Path) -> AcceptedInstall:
    return AcceptedInstall(ACCEPTED_RECORD, _candidate(root))


def _install_equivalence(accepted: AcceptedInstall, current: InstalledCandidate) -> bytes:
    record = install_equivalence_record(
        accepted,
        current,
        record_id="equiv-install-1",
        producer={"tool": "workflow_evidence", "version": "1"},
        created_at="2026-10-24T01:00:00Z",
    )
    return json.dumps(record).encode()


def test_unchanged_install_is_reused_after_a_session_refresh(repo: Path) -> None:
    accepted = _accepted(repo)
    # A refreshed session re-observes the same install; nothing about the session is input.
    decision = install_reuse(accepted, _candidate(repo))

    assert decision.disposition == "valid"
    assert decision.reasons == ()
    assert decision.current_key == decision.accepted_key
    assert decision.equivalence is None


@pytest.mark.parametrize(
    ("artifact", "environment", "disposition", "reason"),
    [
        ({WHEEL: "c" * 64}, {}, "invalid", f"artifact.{WHEEL}_changed"),
        (
            {"installed:harness_core": DIFFERING},
            {},
            "invalid",
            "artifact.installed:harness_core_changed",
        ),
        (
            {"installed:harness_core": "version=0.0.0; editable=true; record=19 verified"},
            {},
            "invalid",
            "artifact.installed:harness_core_changed",
        ),
        (
            {"site_packages": "/elsewhere/site-packages"},
            {},
            "invalid",
            "artifact.site_packages_changed",
        ),
        (
            {},
            {"python": "/usr/bin/python3.12"},
            "impact_review_required",
            "environment.python_changed",
        ),
    ],
)
def test_install_reuse_rejects_changed_distribution_or_pins(
    repo: Path,
    artifact: dict[str, str | None],
    environment: dict[str, str | None],
    disposition: str,
    reason: str,
) -> None:
    decision = install_reuse(_accepted(repo), _candidate(repo, artifact, environment))

    assert decision.disposition == disposition
    assert decision.reasons == (reason,)


def test_changed_installed_inputs_require_impact_review(repo: Path, tmp_path: Path) -> None:
    accepted = _accepted(repo)
    _write(repo, "ops/core.py", "VALUE = 2\n")
    _git(repo, "commit", "-q", "-am", "installed source change")
    current = _candidate(repo)

    decision = install_reuse(accepted, current)
    assert decision.disposition == "impact_review_required"
    assert decision.reasons == ("source.files_changed", "source.equivalence_required")
    # No equivalence can be produced for a changed installed input.
    with pytest.raises(EvidenceError):
        _install_equivalence(accepted, current)


@pytest.mark.parametrize(
    ("accepted_override", "current_override", "disposition", "reasons"),
    [
        ({}, {"origins": None}, "unknown", ("artifact.origins_unknown",)),
        ({"origins": None}, {"origins": None}, "unknown", ("artifact.origins_unknown",)),
        ({}, {"kernel": "7.2.6"}, "unknown", ("artifact.kernel_unknown",)),
        (
            {},
            {"origins": None, WHEEL: "c" * 64},
            "invalid",
            (f"artifact.{WHEEL}_changed", "artifact.origins_unknown"),
        ),
    ],
)
def test_unobserved_install_facts_refuse_reuse_as_unknown(
    repo: Path,
    accepted_override: dict[str, str | None],
    current_override: dict[str, str | None],
    disposition: str,
    reasons: tuple[str, ...],
) -> None:
    accepted = AcceptedInstall(ACCEPTED_RECORD, _candidate(repo, accepted_override))

    decision = install_reuse(accepted, _candidate(repo, current_override))

    assert decision.disposition == disposition
    assert decision.reasons == reasons


def test_gate_only_equivalence_cannot_claim_new_install(repo: Path) -> None:
    accepted = _accepted(repo)
    run = InstalledRun("run-1", "b104-n1", accepted.candidate.key, "passed")
    _write(repo, "tools/checker.py", "print('gate log only')\n")
    _git(repo, "commit", "-q", "-am", "gate-only revision")
    final = _candidate(repo)
    assert final.source.key == accepted.candidate.source.key
    assert final.key != accepted.candidate.key

    without = install_reuse(accepted, final)
    assert without.disposition == "impact_review_required"
    assert without.reasons == ("source.equivalence_required",)
    # The older run is not an unqualified install of the later revision.
    assert bind_acceptance(run, final).reasons == ("candidate_mismatch",)

    equivalence = parse_equivalence(_install_equivalence(accepted, final))
    carried = install_reuse(accepted, final, equivalence)
    assert carried.disposition == "valid"
    binding = bind_acceptance(run, final, carried)
    assert binding.accepted is True
    assert (binding.final_head, binding.run_candidate, binding.equivalence) == (
        final.source.head,
        accepted.candidate.key,
        "equiv-install-1",
    )

    # The same equivalence cannot carry the run to a rebuilt artifact.
    rebuilt = _candidate(repo, {WHEEL: "c" * 64})
    changed = install_reuse(accepted, rebuilt, equivalence)
    assert changed.disposition == "invalid"
    assert bind_acceptance(run, rebuilt, changed).reasons == ("reuse_invalid",)


def test_source_or_build_proof_never_substitutes_for_installed_acceptance(repo: Path) -> None:
    final = _candidate(repo)
    source_proof = _passed_receipt(build_manifest(repo, _request(repo)))
    other = InstalledRun("run-2", "b104-n1", "e" * 64, "passed")

    assert bind_acceptance(source_proof, final).reasons == (
        "source_proof_is_not_installed_acceptance",
    )
    assert bind_acceptance(_accepted(repo), final).reasons == (
        "build_proof_is_not_installed_acceptance",
    )
    assert bind_acceptance(InstalledRun("run-3", "s", final.key, "failed"), final).reasons == (
        "run_not_passed",
    )
    assert bind_acceptance(other, final).reasons == ("candidate_mismatch",)
    # A valid reuse for a different accepted candidate carries nothing to this run.
    unrelated = install_reuse(_accepted(repo), final)
    assert bind_acceptance(other, final, unrelated).reasons == ("candidate_mismatch",)
    direct = bind_acceptance(InstalledRun("run-4", "s", final.key, "passed"), final)
    assert (direct.accepted, direct.equivalence) == (True, None)


def _record_line(site: Path, rel: str) -> str:
    digest = base64.urlsafe_b64encode(hashlib.sha256((site / rel).read_bytes()).digest())
    return f"{rel},sha256={digest.rstrip(b'=').decode()},{(site / rel).stat().st_size}"


def _native_install(tmp_path: Path, head: str) -> tuple[Path, bytes, bytes]:
    """An existing install plus native accepted evidence in its own schema."""
    exec_root = tmp_path / "exec"
    (exec_root / "dist").mkdir(parents=True)
    wheel = exec_root / "dist" / "harness_core-0.0.0-py3-none-any.whl"
    wheel.write_bytes(b"wheel bytes")
    site = exec_root / "venv" / "lib" / "python3.12" / "site-packages"
    info = site / "harness_core-0.0.0.dist-info"
    info.mkdir(parents=True)
    (site / "harness_core").mkdir()
    (site / "harness_core" / "__init__.py").write_text("VALUE = 1\n", encoding="utf-8")
    (info / "METADATA").write_text("Name: harness-core\nVersion: 0.0.0\n", encoding="utf-8")
    lines = [
        _record_line(site, rel) for rel in ("harness_core/__init__.py", f"{info.name}/METADATA")
    ]
    (info / "RECORD").write_text(
        "\n".join([*lines, f"{info.name}/RECORD,,"]) + "\n", encoding="utf-8"
    )
    interpreter = tmp_path / "cpython" / "python3.12"
    interpreter.parent.mkdir()
    interpreter.write_text("", encoding="utf-8")
    (exec_root / "venv" / "bin").mkdir()
    (exec_root / "venv" / "bin" / "python").symlink_to(interpreter)
    result = json.dumps(
        {
            "inputs_verified_before": {"main": f"{head}, 0 tracked/untracked changes"},
            "artifacts": {
                "dist_sha256_file": {
                    "content": [f"{hashlib.sha256(b'wheel bytes').hexdigest()}  {wheel.name}"]
                }
            },
            "installed": {
                "python_realpath": str(interpreter),
                "site_packages": str(site),
                "harness_modules_loaded": 339,
                "all_modules_in_site": True,
                "v1_failures": [],
                "dists": {
                    "harness-core": {
                        "direct_url": None,
                        "record_files_verified": 2,
                        "version": "0.0.0",
                    }
                },
            },
        }
    ).encode()
    acceptance = json.dumps(
        {
            "status": "BUILD_INSTALL_EVIDENCE_ACCEPTED_ONLY",
            "result": {
                "path": "/retained/execution-result.json",
                "sha256": hashlib.sha256(result).hexdigest(),
                "bytes": len(result),
            },
        }
    ).encode()
    return exec_root, acceptance, result


def test_native_accepted_build_matches_the_observed_install(repo: Path, tmp_path: Path) -> None:
    source = build_manifest(repo, _installed_request(repo))
    exec_root, acceptance, result = _native_install(tmp_path, source.head)
    accepted = accepted_build_install(acceptance, result, source)
    assert accepted.record_id == "sha256:" + hashlib.sha256(acceptance).hexdigest()

    def observed(origins: str | None) -> InstalledCandidate:
        artifact, environment = observe_install(exec_root, ("harness_core",), origins)
        return InstalledCandidate(source, artifact, environment)

    origins = "339 harness modules in site-packages"
    assert install_reuse(accepted, observed(origins)).disposition == "valid"
    # The origin check needs the installed interpreter; until observed it stays unknown.
    assert install_reuse(accepted, observed(None)).reasons == ("artifact.origins_unknown",)

    site = exec_root / "venv" / "lib" / "python3.12" / "site-packages"
    (site / "harness_core" / "__init__.py").write_text("VALUE = 2\n", encoding="utf-8")
    tampered = install_reuse(accepted, observed(origins))
    assert tampered.disposition == "invalid"
    assert tampered.reasons == ("artifact.installed:harness_core_changed",)


def test_native_accepted_build_refuses_inconsistent_evidence(repo: Path, tmp_path: Path) -> None:
    source = build_manifest(repo, _installed_request(repo))
    _, acceptance, result = _native_install(tmp_path, source.head)
    pending = json.loads(acceptance)
    pending["status"] = "BUILD_INSTALL_PENDING"
    _write(repo, "ops/core.py", "VALUE = 9\n")
    _git(repo, "commit", "-q", "-am", "later head")
    later = build_manifest(repo, _installed_request(repo))

    for args, field in (
        ((acceptance, result + b" ", source), "acceptance.result"),
        ((json.dumps(pending).encode(), result, source), "acceptance.status"),
        ((acceptance, result, later), "inputs_verified_before.main"),
    ):
        with pytest.raises(EvidenceError) as caught:
            accepted_build_install(*args)
        assert caught.value.field == field


def _contract(candidate: str, **overrides: object) -> dict[str, object]:
    doc: dict[str, object] = {
        "schema_version": 1,
        "scenario": "soak-60",
        "candidate": candidate,
        "argv": ["harness", "run", "--workload", "accepted"],
        "environment": {"OLLAMA_HOST": "127.0.0.1:11434"},
        "capability": "systemd user transient service",
        "workload": SOURCE_REF,
        "expected": {"outcome": "behaves"},
        "thresholds": {"soak_minutes": {"value": "60", "source": SOURCE_REF}},
        "resources": {"process-group": "runtime"},
        "evidence": "/mnt/mac/arhugula-artifacts/soak-60",
        "cleanup": {"precleanup": "no owned process", "postcleanup": "no owned survivor"},
    }
    doc.update(overrides)
    return doc


def _without(doc: dict[str, object], *path: str) -> dict[str, object]:
    copy = json.loads(json.dumps(doc))
    *parents, leaf = path
    target = copy
    for name in parents:
        target = target[name]
    del target[leaf]
    return copy


@pytest.mark.parametrize(
    ("mutate", "field"),
    [
        (lambda d: _without(d, "candidate"), "contract"),
        (lambda d: _without(d, "expected"), "contract"),
        (lambda d: _without(d, "thresholds", "soak_minutes", "source"), "thresholds.soak_minutes"),
        (lambda d: {**d, "thresholds": {}}, "thresholds"),
        (lambda d: {**d, "resources": {}}, "resources"),
        (lambda d: {**d, "resources": {"process-group": ""}}, "resources.process-group"),
        (lambda d: {**d, "evidence": " "}, "evidence"),
        (lambda d: _without(d, "cleanup", "postcleanup"), "cleanup"),
        (lambda d: {**d, "argv": []}, "argv"),
        (lambda d: {**d, "candidate": "unbound"}, "candidate"),
        (lambda d: {**d, "expected": {"outcome": "refuses"}}, "expected"),
    ],
)
def test_incomplete_scenario_contract_refuses_start(mutate, field: str) -> None:
    with pytest.raises(EvidenceError) as caught:
        parse_scenario_contract(json.dumps(mutate(_contract("f" * 64))).encode())
    assert caught.value.field == field


def test_scenario_admission_binds_candidate_and_original_thresholds(repo: Path) -> None:
    candidate = _candidate(repo)
    accepted = {"soak_minutes": Threshold("60", Reference(**SOURCE_REF))}

    def admit(doc: dict[str, object], against: InstalledCandidate = candidate) -> tuple[str, ...]:
        return admit_scenario(parse_scenario_contract(json.dumps(doc).encode()), against, accepted)

    assert admit(_contract(candidate.key)) == ()
    shortened = {"soak_minutes": {"value": "30", "source": SOURCE_REF}}
    assert admit(_contract(candidate.key, thresholds=shortened)) == (
        "threshold.soak_minutes_differs",
    )
    extra = {
        **shortened,
        "soak_minutes": {"value": "60", "source": SOURCE_REF},
        "rss_mb": shortened["soak_minutes"],
    }
    assert admit(_contract(candidate.key, thresholds=extra)) == ("threshold.rss_mb_differs",)
    assert admit(_contract("e" * 64)) == ("candidate_mismatch",)
    unobserved = _candidate(repo, {"origins": None})
    assert admit(_contract(unobserved.key), unobserved) == ("candidate_unknown",)


@pytest.mark.parametrize(
    ("expected", "outcome", "cleaned", "result"),
    [
        (Behaves(), Behaved(), True, "passed"),
        (Behaves(), Behaved(), False, "held"),
        (Behaves(), Refused("timeout"), True, "failed"),
        (Behaves(), Refused("timeout"), False, "failed"),
        (Behaves(), InfrastructureFailed("docker stopped"), True, "error"),
        (Refuses("resume_refused"), Refused("resume_refused"), True, "passed"),
        (Refuses("resume_refused"), Refused("other_refusal"), True, "failed"),
        (Refuses("resume_refused"), Behaved(), True, "failed"),
        (Refuses("resume_refused"), InfrastructureFailed("mount lost"), True, "error"),
    ],
)
def test_scenario_judgment_passes_only_the_specific_expected_outcome(
    expected, outcome, cleaned: bool, result: str
) -> None:
    reference = Reference(**SOURCE_REF)
    observation = ScenarioObservation(outcome, reference, reference if cleaned else None)

    assert judge_scenario(expected, observation) == result
