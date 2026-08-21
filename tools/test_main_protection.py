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
