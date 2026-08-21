"""U-HE-27 (C-HE-08 §2–§5): branch-protection recipes for `main` — the server-side X9 fence.

Provider-free unit tests: payload derivation from ci.yml, GET→PUT normalization, and the
`verify` exact-compare. The live halves (`apply --confirm`, `tiebreaker`) are operator-gated
(spec §3–§4) and recorded in the plan evidence log, not exercised here.
"""

from __future__ import annotations

import sys
from pathlib import Path

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
    assert put == {
        "required_status_checks": {"strict": True, "contexts": ["a — blocking"]},
        "enforce_admins": True,
        "required_pull_request_reviews": None,
        "restrictions": None,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "required_linear_history": False,
    }
    assert mp.verify(got, put) == []
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


def test_merge_refusal_classifier_separates_protection_from_transport():
    """A `gh pr merge` refusal is enforcement evidence only when attributable to branch
    protection / strict base-freshness; auth, rate-limit, and network failures are an
    indeterminate probe, never a PASS (codex r1 P2)."""
    assert mp._merge_refusal_is_protection("GraphQL: Pull request is not mergeable")
    assert mp._merge_refusal_is_protection("Required status check 'x' is expected.")
    assert mp._merge_refusal_is_protection("Head branch is behind the base branch")
    assert not mp._merge_refusal_is_protection("HTTP 401: Bad credentials")
    assert not mp._merge_refusal_is_protection("API rate limit exceeded for user")
    assert not mp._merge_refusal_is_protection("could not resolve host: github.com")


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
