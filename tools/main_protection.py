#!/usr/bin/env python3
"""C-HE-08 §2–§5: server-side X9 fence for `main` as recipes — show / apply / rollback /
verify / tiebreaker.

The required-status-context list is RE-DERIVED from .github/workflows/ci.yml at run time
(job `name:` values ending "— blocking", workflow "CI"), so the payload never drifts from
the workflow. `apply` is operator-gated (one AskUserQuestion with the printed diff) and
refuses to run in loop mode (the permission guard denies `gh api -X` there anyway); a
confirmed apply is PROVISIONAL — the §4 tiebreaker runs immediately and a FAIL rolls the
protection back to the pre-change state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
CI_YML = REPO / ".github" / "workflows" / "ci.yml"
EVIDENCE_LOG = REPO / ".harness" / "plan" / "evidence-log-he-loop-lanes.md"
REQUIRED: dict[str, object] = {
    "required_pull_request_reviews": None,
    "enforce_admins": True,
    "allow_force_pushes": False,
    "allow_deletions": False,
    "required_linear_history": False,
}


def blocking_contexts(ci_yml: Path = CI_YML) -> list[str]:
    ci = yaml.safe_load(ci_yml.read_text())
    assert ci.get("name") == "CI", "workflow name must be CI (status contexts are keyed by it)"
    return sorted(
        j["name"]
        for j in ci["jobs"].values()
        if isinstance(j.get("name"), str) and j["name"].endswith("— blocking")
    )


def desired_payload(contexts: list[str]) -> dict[str, object]:
    # `restrictions` is a REQUIRED nullable field on the PUT (Codex round-5 P1).
    return {
        **REQUIRED,
        "required_status_checks": {"strict": True, "contexts": list(contexts)},
        "restrictions": None,
    }


def _gh(*args: str, timeout: float = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["gh", *args], capture_output=True, text=True, timeout=timeout)


def _repo() -> str:
    return _gh("repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner").stdout.strip()


def current_protection() -> dict | None:
    p = _gh("api", f"repos/{_repo()}/branches/main/protection")
    if p.returncode != 0:
        if "404" in p.stderr or "Branch not protected" in p.stderr:
            return None
        raise SystemExit(f"gh api failed: {p.stderr.strip()}")
    return json.loads(p.stdout)


#: Mutable top-level protection controls beyond the fixed REQUIRED set. A rollback payload
#: must carry these when the captured pre-change policy did — dropping them would restore a
#: WEAKER policy than was live (codex r2 P1). Absent from the §2 desired payload on purpose.
_OPTIONAL_CONTROLS = (
    "required_conversation_resolution",
    "block_creations",
    "lock_branch",
    "allow_fork_syncing",
)


def _flag(cur: dict | None, key: str) -> object:
    v = (cur or {}).get(key)
    return v.get("enabled") if isinstance(v, dict) and "enabled" in v else v


def verify(current: dict | None, desired: dict) -> list[str]:
    """Mismatches of a live GET `current` against a PUT-shaped `desired` — DESIRED-RELATIVE
    throughout (codex r2 P2): the same comparator serves the §2 target policy AND the
    rollback restore-check, where `desired` is the normalized pre-change policy (which may
    legitimately carry reviews or restrictions)."""
    if current is None:
        return ["unprotected (404)"]
    out: list[str] = []
    want_rsc = desired.get("required_status_checks")
    rsc = current.get("required_status_checks") or {}
    if want_rsc is None:
        if rsc:
            out.append("required_status_checks must be absent")
    else:
        if rsc.get("strict") is not want_rsc["strict"]:
            out.append(
                f"required_status_checks.strict: {rsc.get('strict')!r} != {want_rsc['strict']!r}"
            )
        if "checks" in want_rsc:
            # App-bound target (a restored prior policy): compare (context, app_id) pairs so
            # an any-app policy is never certified as an app-bound one (codex r3 P2).
            have_pairs = sorted((c["context"], c.get("app_id")) for c in rsc.get("checks") or [])
            want_pairs = sorted((c["context"], c.get("app_id")) for c in want_rsc["checks"])
            if have_pairs != want_pairs:
                out.append(
                    f"checks differ: missing={sorted(set(want_pairs) - set(have_pairs))} "
                    f"extra={sorted(set(have_pairs) - set(want_pairs))}"
                )
        else:
            have = sorted(rsc.get("contexts") or [c["context"] for c in rsc.get("checks", [])])
            want = sorted(want_rsc["contexts"])
            if have != want:
                out.append(
                    f"contexts differ: missing={sorted(set(want) - set(have))} "
                    f"extra={sorted(set(have) - set(want))}"
                )
    want_prr = desired.get("required_pull_request_reviews")
    cur_prr = current.get("required_pull_request_reviews")
    if want_prr is None:
        if cur_prr not in (None, {}):
            out.append(
                "required_pull_request_reviews must be null (review authority is the gate chain)"
            )
    elif _prr_put_payload(cur_prr or {}) != want_prr:
        out.append("required_pull_request_reviews differ from the target policy")
    for k in ("enforce_admins", "allow_force_pushes", "allow_deletions", "required_linear_history"):
        if _flag(current, k) != desired[k]:
            out.append(f"{k}: {_flag(current, k)!r} != {desired[k]!r}")
    # Optional strengthening controls are ALWAYS compared: a target that omits them pins
    # them to their default (False) — otherwise a live lock_branch would verify PASS while
    # blocking every PR landing (codex r3 P2). An absent key on the live side reads False.
    for k in _OPTIONAL_CONTROLS:
        if bool(_flag(current, k)) != bool(desired.get(k, False)):
            out.append(f"{k}: {bool(_flag(current, k))!r} != {bool(desired.get(k, False))!r}")
    # §2 exact-compare includes restrictions: the target payload pins them (null for §2), so
    # a live user/team/app push restriction is a mismatch, not an ignorable extra (codex r1 P2).
    want_r = desired.get("restrictions")
    cur_r = _restrictions_payload(current.get("restrictions"))
    if want_r is None:
        if cur_r:
            out.append("restrictions must be null (no user/team/app push restrictions)")
    elif cur_r != want_r:
        out.append("restrictions differ from the target policy")
    return out


def _restrictions_payload(r: dict | None) -> dict | None:
    if not r:
        return None
    return {
        "users": [u["login"] for u in r.get("users", [])],
        "teams": [t["slug"] for t in r.get("teams", [])],
        "apps": [a["slug"] for a in r.get("apps", [])],
    }


def _prr_put_payload(prr: dict) -> dict:
    """PUT-shaped required_pull_request_reviews, preserving the optional strengthening fields
    (dismissal_restrictions / bypass_pull_request_allowances / require_last_push_approval) so a
    rollback never restores a WEAKER review policy than was captured (codex r1 P2)."""
    out: dict = {
        "dismiss_stale_reviews": bool(prr.get("dismiss_stale_reviews")),
        "require_code_owner_reviews": bool(prr.get("require_code_owner_reviews")),
        "required_approving_review_count": int(prr.get("required_approving_review_count", 0)),
        "require_last_push_approval": bool(prr.get("require_last_push_approval")),
    }
    if prr.get("dismissal_restrictions"):
        out["dismissal_restrictions"] = _restrictions_payload(prr["dismissal_restrictions"]) or {}
    if prr.get("bypass_pull_request_allowances"):
        out["bypass_pull_request_allowances"] = (
            _restrictions_payload(prr["bypass_pull_request_allowances"]) or {}
        )
    return out


def _to_put_payload(got: dict) -> dict:
    """The GET response is not a valid PUT body (nested response objects, read-only urls);
    normalize to the fields the PUT accepts so a rollback actually restores (Codex round-4 P1)."""
    rsc = got.get("required_status_checks") or {}
    prr = got.get("required_pull_request_reviews")
    if not rsc:
        put_rsc = None
    elif rsc.get("checks"):
        # Preserve per-check app bindings — flattening checks to bare contexts would restore
        # an app-bound prior policy as an any-app policy (codex r3 P2). A null app_id means
        # "any app" and is expressed by omitting the key on the PUT.
        put_rsc = {
            "strict": bool(rsc.get("strict")),
            "checks": sorted(
                (
                    {
                        "context": c["context"],
                        **({"app_id": c["app_id"]} if c.get("app_id") is not None else {}),
                    }
                    for c in rsc["checks"]
                ),
                key=lambda c: (c["context"], c.get("app_id") or 0),
            ),
        }
    else:
        put_rsc = {"strict": bool(rsc.get("strict")), "contexts": sorted(rsc.get("contexts") or [])}
    return {
        "required_status_checks": put_rsc,
        "enforce_admins": bool(_flag(got, "enforce_admins")),
        "required_pull_request_reviews": (None if not prr else _prr_put_payload(prr)),
        # Preserve user/team/app restrictions on rollback (round-5 P1).
        "restrictions": _restrictions_payload(got.get("restrictions")),
        "allow_force_pushes": bool(_flag(got, "allow_force_pushes")),
        "allow_deletions": bool(_flag(got, "allow_deletions")),
        "required_linear_history": bool(_flag(got, "required_linear_history")),
        # Optional strengthening controls survive the normalization when captured (r2 P1).
        **{k: bool(_flag(got, k)) for k in _OPTIONAL_CONTROLS if k in got},
    }


def _approval_digest(current: dict | None, desired: dict) -> str:
    """Binds an operator approval to the exact (BEFORE, AFTER) pair shown at the dry run."""
    blob = json.dumps([current, desired], sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def diff_report(current: dict | None, desired: dict) -> str:
    return (
        "BEFORE:\n"
        + json.dumps(current, indent=2, sort_keys=True)
        + "\nAFTER:\n"
        + json.dumps(desired, indent=2, sort_keys=True)
    )


def _loop_mode() -> bool:
    return os.environ.get("HARNESS_LOOP") == "1" or (REPO / ".harness" / ".loop-active").exists()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["show", "apply", "rollback", "verify", "tiebreaker"])
    p.add_argument("--confirm", action="store_true")
    p.add_argument("--approved-digest", default=None)
    a = p.parse_args(argv)
    desired = desired_payload(blocking_contexts())
    if a.cmd == "verify":
        if _gh("auth", "status").returncode != 0:
            # A legal §8.1 skip; lanes-phase0-check counts it RED (C-HE-13 §1).
            print("SKIPPED [1] main_protection.py:1: gh-auth-absent")
            return 0
        try:
            cur = current_protection()
        except SystemExit as e:
            # Logged in but the token lacks the scope to READ protection (403): that is the
            # same auth-insufficient class as no login — the contractual skip, not a hard
            # failure (codex r1 P3).
            if "403" in str(e) or "Resource not accessible" in str(e):
                print("SKIPPED [1] main_protection.py:1: gh-auth-absent")
                return 0
            raise
        problems = verify(cur, desired)
        for m in problems:
            print(f"MISMATCH {m}")
        print("main-protection-verify:", "PASS" if not problems else "FAIL")
        return 1 if problems else 0
    if a.cmd == "show":
        print(json.dumps(current_protection(), indent=2, sort_keys=True))
        return 0
    if a.cmd == "apply":
        if _loop_mode():
            raise SystemExit(
                "apply refuses to run in loop mode (operator-gated; CLAUDE.md §12.4.1)"
            )
        cur = current_protection()
        digest = _approval_digest(cur, desired)
        print(diff_report(cur, desired))
        if not a.confirm:
            print(
                f"\nDRY RUN — nothing changed. approval digest: {digest}\n"
                "After the operator approves THIS diff, run "
                f"`just main-protection-apply-confirm {digest}`."
            )
            return 3
        # The confirmation is bound to the exact BEFORE/AFTER pair the operator approved:
        # if the live protection or the ci.yml-derived payload changed between the dry run
        # and this confirm, the digest differs and NOTHING is mutated (codex r2 P1).
        if a.approved_digest != digest:
            raise SystemExit(
                "approval digest mismatch: the live protection or the ci.yml-derived payload "
                f"changed since the approved diff (approved={a.approved_digest or '<none>'}, "
                f"current={digest}) — re-run `just main-protection-apply` and re-approve"
            )
        stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with EVIDENCE_LOG.open("a") as f:
            f.write(f"\n## main-protection apply {stamp}\n```\n{diff_report(cur, desired)}\n```\n")
        r = subprocess.run(
            ["gh", "api", "-X", "PUT", f"repos/{_repo()}/branches/main/protection", "--input", "-"],
            input=json.dumps(desired),
            capture_output=True,
            text=True,
            timeout=60,
        )
        if r.returncode != 0:
            raise SystemExit(f"apply failed: {r.stderr.strip()}")
        # C-HE-08 §4: the settings are exercised BEFORE they are allowed to persist. The
        # tiebreaker needs strict:true live to be meaningful, so apply is provisional: a FAIL
        # rolls back to the pre-change state (Codex round-3 P1).
        print("applied provisionally; running the tiebreaker (FAIL → automatic rollback)")
        try:
            rc = tiebreaker()
        except BaseException as e:  # sh() raises SystemExit; subprocess raises
            # TimeoutExpired. ANY escape after the PUT must still reach the rollback below —
            # exiting here would leave the new protection silently live (codex r1 P1).
            rc = 1
            print(f"tiebreaker raised instead of returning: {e!r}")
        if rc != 0:
            if cur is None:
                # Pre-change state was unprotected: DELETE, and VALIDATE that the deletion
                # actually landed — a failed DELETE must not be reported as a rollback (r1 P2).
                rb = _gh(
                    "api", "-X", "DELETE", f"repos/{_repo()}/branches/main/protection", timeout=60
                )
                if rb.returncode != 0 or current_protection() is not None:
                    raise SystemExit(
                        "tiebreaker FAILED and the rollback DELETE did not restore the "
                        "unprotected pre-change state — the new protection REMAINS LIVE on "
                        "main; run `just main-protection-rollback` and re-verify "
                        f"({rb.stderr.strip()[:200]})"
                    )
                raise SystemExit(
                    "tiebreaker FAILED → protection rolled back (DELETE); settings NOT persisted"
                )
            # Prior policy exists: restore it with a single PUT — PUT replaces in place, so
            # there is no reason to open an unprotected DELETE window first (codex r2 P1).
            restore = subprocess.run(
                [
                    "gh",
                    "api",
                    "-X",
                    "PUT",
                    f"repos/{_repo()}/branches/main/protection",
                    "--input",
                    "-",
                ],
                input=json.dumps(_to_put_payload(cur)),
                capture_output=True,
                text=True,
                timeout=60,
            )
            if restore.returncode != 0 or verify(current_protection(), _to_put_payload(cur)):
                raise SystemExit(
                    "tiebreaker FAILED and the prior protection could NOT be verified as "
                    "restored — inspect `just main-protection-show` against the evidence-log "
                    "BEFORE block and restore by hand "
                    f"({restore.stderr.strip()[:200]})"
                )
            raise SystemExit(
                "tiebreaker FAILED → prior protection restored (PUT); new settings NOT persisted"
            )
        print("tiebreaker PASS; protection persists. Run `just main-protection-verify`.")
        return 0
    if a.cmd == "rollback":
        r = _gh("api", "-X", "DELETE", f"repos/{_repo()}/branches/main/protection", timeout=60)
        print("rolled back (pre-change show output is in the evidence log)")
        return r.returncode
    # tiebreaker: scratch PR under strict:true + stale-refresh-branch check (HE-1 O4; C10-T8).
    if _loop_mode():
        raise SystemExit("tiebreaker is a live probe; run outside loop mode")
    return tiebreaker()


#: Three-way refusal attribution (codex r1 P2 + r3 P2). "strict" signatures name the
#: protection/base-freshness mechanism itself; "generic" signatures ("not mergeable",
#: "merge state") also cover conflicts and unrelated restrictions, so they count as
#: enforcement evidence only when the PR's own mergeStateStatus independently read BEHIND
#: (the strict staleness reading); anything else (auth/rate-limit/network/head-race) is an
#: indeterminate probe, never a PASS.
_STRICT_REFUSAL_SIGS = (
    "required status check",
    "branch protection",
    "protected branch",
    "behind",
    "base branch",
    "review is required",
)
_GENERIC_MERGEABILITY_SIGS = ("not mergeable", "merge state")


def _classify_merge_refusal(stderr: str) -> str:
    """'strict' | 'generic' | 'transport' — see the signature-tier comment above."""
    low = stderr.lower()
    if any(s in low for s in _STRICT_REFUSAL_SIGS):
        return "strict"
    if any(s in low for s in _GENERIC_MERGEABILITY_SIGS):
        return "generic"
    return "transport"


def tiebreaker() -> int:
    """C-HE-08 §4 (HE-1 O4; C10-T8): exercise strict:true on a scratch PR, then the
    load-bearing parameter — a refresh-shaped PR branched from the since-superseded main is
    CAUGHT pre-merge or fast-forwards cleanly.

    Runs in an ISOLATED temporary worktree (never switches the operator's checkout; never
    picks up staged changes — Codex round-3 P1) and compares the stale landing against the
    main SHA captured BEFORE that merge."""
    # PID suffix: one-second timestamp uniqueness is not enough — concurrent tiebreakers
    # must never collide on (or GC) each other's scratch branches (codex r3 P2).
    ts = f"{time.strftime('%Y%m%d%H%M%S', time.gmtime())}-{os.getpid()}"
    br = f"mp-tiebreaker-{ts}"
    br2 = f"mp-tiebreaker-stale-{ts}"
    wt = Path(tempfile.mkdtemp(prefix="mp-tiebreaker-"))
    created: list[str] = []  # only branches THIS invocation pushed are GC'd (codex r3 P2)

    def sh(*c: str, cwd: Path | None = None) -> str:
        q = subprocess.run(list(c), capture_output=True, text=True, timeout=180, cwd=cwd or wt)
        if q.returncode != 0:
            raise SystemExit(f"{' '.join(c)}: {q.stderr.strip()}")
        return q.stdout.strip()

    sh("git", "fetch", "-q", "origin", cwd=REPO)
    sh("git", "worktree", "add", "-q", "--detach", str(wt), "origin/main", cwd=REPO)
    try:
        base = sh("git", "rev-parse", "origin/main")
        sh("git", "checkout", "-q", "-b", br)
        sh("git", "commit", "-q", "--allow-empty", "-m", f"chore: main-protection tiebreaker {ts}")
        sh("git", "push", "-q", "-u", "origin", br)
        created.append(br)
        url = sh(
            "gh",
            "pr",
            "create",
            "--title",
            f"chore: main-protection tiebreaker {ts}",
            "--body",
            "scratch PR; C-HE-08 §4",
        )
        pr = url.rsplit("/", 1)[-1]
        print(f"tiebreaker: waiting for checks on #{pr} (strict:true requires up-to-date + green)")
        sh("gh", "pr", "checks", pr, "--watch")
        head = sh("git", "rev-parse", "HEAD")
        m = subprocess.run(
            ["gh", "pr", "merge", pr, "--squash", "--match-head-commit", head],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=wt,
        )
        if m.returncode != 0:
            print(
                f"precondition failed: scratch merge refused under strict:true ({m.stderr.strip()})"
            )
            return 1
        # The load-bearing parameter: a refresh-shaped PR branched from the since-superseded main.
        sh("git", "checkout", "-q", "-b", br2, base)
        sh("git", "commit", "-q", "--allow-empty", "-m", "ops: stale refresh-shaped commit")
        sh("git", "push", "-q", "-u", "origin", br2)
        created.append(br2)
        url2 = sh(
            "gh",
            "pr",
            "create",
            "--title",
            f"chore: stale-base tiebreaker {ts}",
            "--body",
            "C-HE-08 §4 stale-branch check",
        )
        pr2 = url2.rsplit("/", 1)[-1]
        # BLOCKED is ambiguous straight after creation — pending or failing required checks
        # also report BLOCKED, so an immediate read could "PASS" without strict:true ever
        # being exercised (codex r1 P1). Let the stale PR's checks settle first, then read.
        chk = subprocess.run(
            ["gh", "pr", "checks", pr2, "--watch"],
            capture_output=True,
            text=True,
            timeout=1800,
            cwd=wt,
        )
        state = sh(
            "gh", "pr", "view", pr2, "--json", "mergeStateStatus", "--jq", ".mergeStateStatus"
        )
        if chk.returncode != 0:
            # Non-green checks contaminate the probe: any merge refusal would be attributable
            # to failing checks rather than base-staleness, so strict:true is not isolable.
            verdict, why = (
                "FAIL",
                f"indeterminate: stale PR checks did not go green (gh pr checks "
                f"rc={chk.returncode}, mergeStateStatus={state}) — strict:true not exercised",
            )
        else:
            # EXERCISE the merge rather than inferring from mergeStateStatus — BEHIND/BLOCKED
            # are advisory readings, and only an actual protection-attributed refusal (or a
            # clean fast-forward landing) proves the load-bearing parameter (codex r2 P1).
            sh("git", "fetch", "-q", "origin")
            pre = sh("git", "rev-parse", "origin/main")  # main BEFORE the stale merge
            head2 = sh("git", "rev-parse", "HEAD")
            m2 = subprocess.run(
                ["gh", "pr", "merge", pr2, "--squash", "--match-head-commit", head2],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=wt,
            )
            if m2.returncode != 0:
                err = m2.stderr.strip()
                kind = _classify_merge_refusal(err)
                if kind == "strict" or (kind == "generic" and state == "BEHIND"):
                    # A generic refusal ("not mergeable") counts only when the independent
                    # mergeStateStatus read said BEHIND — the strict staleness signal (r3 P2).
                    verdict, why = (
                        "PASS",
                        f"stale merge REFUSED under strict:true "
                        f"(mergeStateStatus={state}; {err[:120]})",
                    )
                else:
                    # Auth / rate-limit / network / head-race failures — and generic
                    # mergeability errors without the BEHIND reading — are NOT enforcement
                    # evidence; an unattributable refusal is an indeterminate probe (r1 P2).
                    verdict, why = (
                        "FAIL",
                        f"indeterminate: stale merge refusal not attributable to strict "
                        f"base-freshness (kind={kind}, mergeStateStatus={state}; {err[:160]})",
                    )
            else:
                sh("git", "fetch", "-q", "origin")
                new_main = sh("git", "rev-parse", "origin/main")
                first_parent = sh("git", "rev-parse", f"{new_main}^1")
                verdict, why = (
                    ("PASS", "stale PR fast-forwarded cleanly onto the pre-merge main")
                    if first_parent == pre
                    else (
                        "FAIL",
                        f"stale PR landed off the pre-merge main "
                        f"(first parent {first_parent[:12]} != {pre[:12]})",
                    )
                )
        print(f"tiebreaker: {verdict} — {why}")
        subprocess.run(
            ["gh", "pr", "close", pr2, "--delete-branch"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=wt,
        )
        return 0 if verdict == "PASS" else 1
    finally:
        # Best-effort external-state GC on EVERY exit path — a failed probe must not leave
        # scratch PRs open or remote branches behind (codex r1 P3): deleting a remote branch
        # auto-closes its open PR, and an already-deleted/merged branch makes this a no-op.
        for scratch in created:
            subprocess.run(
                ["git", "push", "-q", "origin", "--delete", scratch],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=REPO,
            )
        subprocess.run(
            ["bash", str(REPO / "tools" / "hooks" / "safe-worktree-remove.sh"), str(wt)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )


if __name__ == "__main__":
    raise SystemExit(main())
