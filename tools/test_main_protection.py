"""U-HE-27 (C-HE-08 §2–§5): branch-protection recipes for `main` — the server-side X9 fence.

Provider-free unit tests: payload derivation from ci.yml, GET→PUT normalization, and the
`verify` exact-compare. The live halves (`apply --confirm`, `tiebreaker`) are operator-gated
(spec §3–§4) and recorded in the plan evidence log, not exercised here.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import main_protection as mp


def test_blocking_contexts_derived_from_ci_yml():
    ctx = mp.blocking_contexts()
    assert "pytest (all axis packages) — blocking" in ctx
    assert all(c.endswith("— blocking") for c in ctx)
    assert len(ctx) >= 12


def test_desired_payload_shape():
    p = mp.desired_payload(["a — blocking"])
    assert p["required_pull_request_reviews"] is None
    assert p["required_status_checks"] == {"strict": True, "contexts": ["a — blocking"]}
    assert "restrictions" in p and p["restrictions"] is None
    assert p["enforce_admins"] is True
    assert p["allow_force_pushes"] is False
    assert p["allow_deletions"] is False
    assert p["required_linear_history"] is False


def test_to_put_payload_normalizes_get_shape():
    got = {
        "url": "x",
        "required_status_checks": {
            "url": "y",
            "strict": True,
            "contexts": ["a — blocking"],
            "checks": [{"context": "a — blocking", "app_id": 1}],
        },
        "enforce_admins": {"url": "z", "enabled": True},
        "required_pull_request_reviews": None,
        "allow_force_pushes": {"enabled": False},
        "allow_deletions": {"enabled": False},
        "required_linear_history": {"enabled": False},
    }
    put = mp._to_put_payload(got)
    # App bindings survive the normalization (codex r3 P2): the GET carried `checks` with an
    # app_id, so the PUT body keeps the pair rather than flattening to any-app contexts.
    assert put == {
        "required_status_checks": {
            "strict": True,
            "checks": [{"context": "a — blocking", "app_id": 1}],
        },
        "enforce_admins": True,
        "required_pull_request_reviews": None,
        "restrictions": None,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "required_linear_history": False,
    }
    assert mp.verify(got, put) == []
    # A null app_id means "any app" and is expressed by omitting the key on the PUT.
    got_anyapp = dict(got)
    got_anyapp["required_status_checks"] = {
        "strict": True,
        "checks": [{"context": "a — blocking", "app_id": None}],
    }
    put_anyapp = mp._to_put_payload(got_anyapp)
    assert put_anyapp["required_status_checks"] == {
        "strict": True,
        "checks": [{"context": "a — blocking"}],
    }
    assert mp.verify(got_anyapp, put_anyapp) == []
    got["restrictions"] = {
        "users": [{"login": "alice"}],
        "teams": [{"slug": "core"}],
        "apps": [],
    }
    assert mp._to_put_payload(got)["restrictions"] == {
        "users": ["alice"],
        "teams": ["core"],
        "apps": [],
    }


def test_verify_flags_live_restrictions():
    """§2 exact-compare: desired pins restrictions to null, so a live user/team/app push
    restriction must be a mismatch — not an ignorable extra (codex r1 P2)."""
    d = mp.desired_payload(["a — blocking"])
    cur = {
        "required_status_checks": {"strict": True, "contexts": ["a — blocking"]},
        "enforce_admins": {"enabled": True},
        "required_pull_request_reviews": None,
        "allow_force_pushes": {"enabled": False},
        "allow_deletions": {"enabled": False},
        "required_linear_history": {"enabled": False},
    }
    assert mp.verify(cur, d) == []
    cur["restrictions"] = {"users": [{"login": "alice"}], "teams": [], "apps": []}
    assert any("restrictions" in m for m in mp.verify(cur, d))


def test_prr_put_payload_preserves_strengthening_fields():
    """Rollback must never restore a WEAKER review policy than captured (codex r1 P2):
    require_last_push_approval / dismissal_restrictions / bypass allowances survive the
    GET→PUT normalization."""
    got = {
        "required_status_checks": {"strict": True, "contexts": ["a — blocking"]},
        "enforce_admins": {"enabled": True},
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": False,
            "required_approving_review_count": 2,
            "require_last_push_approval": True,
            "dismissal_restrictions": {"users": [{"login": "alice"}], "teams": [{"slug": "core"}]},
            "bypass_pull_request_allowances": {"users": [], "teams": [], "apps": [{"slug": "bot"}]},
        },
        "allow_force_pushes": {"enabled": False},
        "allow_deletions": {"enabled": False},
        "required_linear_history": {"enabled": False},
    }
    prr = mp._to_put_payload(got)["required_pull_request_reviews"]
    assert prr["required_approving_review_count"] == 2
    assert prr["require_last_push_approval"] is True
    assert prr["dismissal_restrictions"] == {"users": ["alice"], "teams": ["core"], "apps": []}
    assert prr["bypass_pull_request_allowances"] == {"users": [], "teams": [], "apps": ["bot"]}


def test_merge_refusal_classifier_three_tiers():
    """'strict' names the protection mechanism itself; 'generic' mergeability errors also
    cover conflicts/unrelated restrictions and count only alongside an independent BEHIND
    reading; transport failures are an indeterminate probe, never a PASS (codex r1/r3 P2)."""
    assert mp._classify_merge_refusal("Required status check 'x' is expected.") == "strict"
    assert mp._classify_merge_refusal("Head branch is behind the base branch") == "strict"
    assert mp._classify_merge_refusal("GraphQL: Pull request is not mergeable") == "generic"
    assert mp._classify_merge_refusal("pull request is in an unstable merge state") == "generic"
    assert mp._classify_merge_refusal("HTTP 401: Bad credentials") == "transport"
    assert mp._classify_merge_refusal("API rate limit exceeded for user") == "transport"
    assert mp._classify_merge_refusal("could not resolve host: github.com") == "transport"
    # head-race is deliberately NOT protection evidence (r2 P2)
    assert mp._classify_merge_refusal("expected head to be abc123 but was def456") == "transport"


_PRIOR_GET = {
    "required_status_checks": {"strict": True, "contexts": ["a — blocking"]},
    "enforce_admins": {"enabled": True},
    "required_pull_request_reviews": None,
    "allow_force_pushes": {"enabled": False},
    "allow_deletions": {"enabled": False},
    "required_linear_history": {"enabled": False},
}


def _wire_apply(monkeypatch, tmp_path, *, cur, tiebreaker):
    """Hermetic apply harness: records every gh/api subprocess, never leaves the process."""
    calls: list[list[str]] = []

    def fake_run(cmd, **kw):
        calls.append(list(cmd))
        return subprocess.CompletedProcess(cmd, 0, "", "")

    def fake_gh(*args, timeout=30):
        calls.append(["gh", *args])
        return subprocess.CompletedProcess(["gh", *args], 0, "", "")

    monkeypatch.setattr(mp.subprocess, "run", fake_run)
    monkeypatch.setattr(mp, "_gh", fake_gh)
    monkeypatch.setattr(mp, "_repo", lambda: "o/r")
    monkeypatch.setattr(mp, "_loop_mode", lambda: False)
    monkeypatch.setattr(mp, "current_protection", lambda: cur)
    monkeypatch.setattr(mp, "tiebreaker", tiebreaker)
    monkeypatch.setattr(mp, "EVIDENCE_LOG", tmp_path / "evidence.md")
    return calls


def _puts(calls):
    return [c for c in calls if "PUT" in c]


def _deletes(calls):
    return [c for c in calls if "DELETE" in c]


def test_apply_confirm_refuses_stale_approval_digest(monkeypatch, tmp_path):
    """The confirm is bound to the exact approved BEFORE/AFTER pair: a digest mismatch must
    abort BEFORE any mutation (codex r2 P1)."""
    calls = _wire_apply(monkeypatch, tmp_path, cur=None, tiebreaker=lambda: 0)
    with pytest.raises(SystemExit) as e:
        mp.main(["apply", "--confirm", "--approved-digest", "0000000000000000"])
    assert "digest mismatch" in str(e.value)
    assert _puts(calls) == [] and _deletes(calls) == []


def test_apply_rollback_deletes_only_when_previously_unprotected(monkeypatch, tmp_path):
    """cur=None + tiebreaker FAIL → exactly one PUT (the provisional apply), a validated
    DELETE, and NO restore PUT (codex r2 P1 sequencing)."""
    calls = _wire_apply(monkeypatch, tmp_path, cur=None, tiebreaker=lambda: 1)
    digest = mp._approval_digest(None, mp.desired_payload(mp.blocking_contexts()))
    with pytest.raises(SystemExit) as e:
        mp.main(["apply", "--confirm", "--approved-digest", digest])
    assert "rolled back" in str(e.value)
    assert len(_puts(calls)) == 1 and len(_deletes(calls)) == 1


def test_apply_rollback_restores_prior_policy_via_put_without_delete(monkeypatch, tmp_path):
    """cur=prior + tiebreaker FAIL → the prior policy is restored with a single PUT and NO
    DELETE — PUT replaces in place, so an unprotected window must never be opened (r2 P1)."""
    calls = _wire_apply(monkeypatch, tmp_path, cur=_PRIOR_GET, tiebreaker=lambda: 1)
    digest = mp._approval_digest(_PRIOR_GET, mp.desired_payload(mp.blocking_contexts()))
    with pytest.raises(SystemExit) as e:
        mp.main(["apply", "--confirm", "--approved-digest", digest])
    assert "prior protection restored" in str(e.value)
    assert len(_puts(calls)) == 2 and _deletes(calls) == []


def test_apply_rolls_back_when_tiebreaker_raises(monkeypatch, tmp_path):
    """A tiebreaker that ESCAPES (SystemExit from sh(), TimeoutExpired) must still reach the
    rollback — never exit with the new protection silently live (codex r1 P1)."""

    def raising_tiebreaker():
        raise SystemExit("gh pr checks: boom")

    calls = _wire_apply(monkeypatch, tmp_path, cur=None, tiebreaker=raising_tiebreaker)
    digest = mp._approval_digest(None, mp.desired_payload(mp.blocking_contexts()))
    with pytest.raises(SystemExit) as e:
        mp.main(["apply", "--confirm", "--approved-digest", digest])
    assert "rolled back" in str(e.value)
    assert len(_deletes(calls)) == 1


def test_verify_restore_check_accepts_prior_policy_with_reviews():
    """The restore-check compares against the NORMALIZED PRIOR policy, not the §2 target: a
    restored policy carrying reviews/restrictions must verify clean (codex r2 P2)."""
    got = {
        "required_status_checks": {"strict": True, "contexts": ["a — blocking"]},
        "enforce_admins": {"enabled": True},
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": False,
            "required_approving_review_count": 1,
        },
        "restrictions": {"users": [{"login": "alice"}], "teams": [], "apps": []},
        "allow_force_pushes": {"enabled": False},
        "allow_deletions": {"enabled": False},
        "required_linear_history": {"enabled": True},
        "required_conversation_resolution": {"enabled": True},
    }
    put = mp._to_put_payload(got)
    assert put["required_conversation_resolution"] is True
    assert mp.verify(got, put) == []


def test_verify_flags_404_and_mismatch():
    d = mp.desired_payload(["a — blocking"])
    assert mp.verify(None, d) == ["unprotected (404)"]
    cur = {
        "required_status_checks": {"strict": False, "contexts": ["a — blocking"]},
        "enforce_admins": {"enabled": True},
        "required_pull_request_reviews": None,
        "allow_force_pushes": {"enabled": False},
        "allow_deletions": {"enabled": False},
        "required_linear_history": {"enabled": False},
    }
    assert any("strict" in m for m in mp.verify(cur, d))
    cur["required_status_checks"]["strict"] = True
    assert mp.verify(cur, d) == []
