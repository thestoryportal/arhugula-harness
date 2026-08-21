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


def _flag(cur: dict | None, key: str) -> object:
    v = (cur or {}).get(key)
    return v.get("enabled") if isinstance(v, dict) and "enabled" in v else v


def verify(current: dict | None, desired: dict) -> list[str]:
    if current is None:
        return ["unprotected (404)"]
    out: list[str] = []
    rsc = current.get("required_status_checks") or {}
    if rsc.get("strict") is not True:
        out.append(f"required_status_checks.strict: {rsc.get('strict')!r} != True")
    have = sorted(rsc.get("contexts") or [c["context"] for c in rsc.get("checks", [])])
    want = sorted(desired["required_status_checks"]["contexts"])
    if have != want:
        out.append(
            f"contexts differ: missing={sorted(set(want) - set(have))} "
            f"extra={sorted(set(have) - set(want))}"
        )
    if current.get("required_pull_request_reviews") not in (None, {}):
        out.append(
            "required_pull_request_reviews must be null (review authority is the gate chain)"
        )
    for k in ("enforce_admins", "allow_force_pushes", "allow_deletions", "required_linear_history"):
        if _flag(current, k) != desired[k]:
            out.append(f"{k}: {_flag(current, k)!r} != {desired[k]!r}")
    # §2 exact-compare includes restrictions: the desired payload pins them to null, so a live
    # user/team/app push restriction is a mismatch, not an ignorable extra (codex r1 P2).
    if current.get("restrictions"):
        out.append("restrictions must be null (no user/team/app push restrictions)")
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
    return {
        "required_status_checks": (
            {
                "strict": bool(rsc.get("strict")),
                "contexts": sorted(
                    rsc.get("contexts") or [c["context"] for c in rsc.get("checks", [])]
                ),
            }
            if rsc
            else None
        ),
        "enforce_admins": bool(_flag(got, "enforce_admins")),
        "required_pull_request_reviews": (None if not prr else _prr_put_payload(prr)),
        # Preserve user/team/app restrictions on rollback (round-5 P1).
        "restrictions": _restrictions_payload(got.get("restrictions")),
        "allow_force_pushes": bool(_flag(got, "allow_force_pushes")),
        "allow_deletions": bool(_flag(got, "allow_deletions")),
        "required_linear_history": bool(_flag(got, "required_linear_history")),
    }


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
        print(diff_report(cur, desired))
        if not a.confirm:
            print(
                "\nDRY RUN — nothing changed. After the operator approves THIS diff, "
                "run `just main-protection-apply-confirm`."
            )
            return 3
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
            rb = _gh("api", "-X", "DELETE", f"repos/{_repo()}/branches/main/protection", timeout=60)
            if cur is None and (rb.returncode != 0 or current_protection() is not None):
                raise SystemExit(
                    "tiebreaker FAILED and the rollback DELETE did not restore the unprotected "
                    "pre-change state — the new protection REMAINS LIVE on main; run "
                    f"`just main-protection-rollback` and re-verify ({rb.stderr.strip()[:200]})"
                )
            if cur is not None:
                # There was a prior protection: restore it from a NORMALIZED (PUT-shaped) payload.
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
                        "tiebreaker FAILED and prior protection could NOT be restored — main is "
                        "UNPROTECTED; re-run apply-confirm or restore by hand "
                        f"({restore.stderr.strip()[:200]})"
                    )
            raise SystemExit(
                f"tiebreaker FAILED → protection rolled back (rc={rb.returncode}); "
                "settings NOT persisted"
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


#: stderr signatures that attribute a `gh pr merge` refusal to branch protection / strict
#: base-freshness enforcement, as opposed to auth/network/rate-limit/head-race failures. A
#: refusal that matches none of these is an INDETERMINATE probe, not a PASS (codex r1 P2).
_PROTECTION_REFUSAL_SIGS = (
    "not mergeable",
    "required status check",
    "branch protection",
    "protected branch",
    "behind",
    "base branch",
    "expected head",
    "review is required",
    "merge state",
)


def _merge_refusal_is_protection(stderr: str) -> bool:
    low = stderr.lower()
    return any(s in low for s in _PROTECTION_REFUSAL_SIGS)


def tiebreaker() -> int:
    """C-HE-08 §4 (HE-1 O4; C10-T8): exercise strict:true on a scratch PR, then the
    load-bearing parameter — a refresh-shaped PR branched from the since-superseded main is
    CAUGHT pre-merge or fast-forwards cleanly.

    Runs in an ISOLATED temporary worktree (never switches the operator's checkout; never
    picks up staged changes — Codex round-3 P1) and compares the stale landing against the
    main SHA captured BEFORE that merge."""
    ts = time.strftime("%Y%m%d%H%M%S", time.gmtime())
    br = f"mp-tiebreaker-{ts}"
    br2 = f"mp-tiebreaker-stale-{ts}"
    wt = Path(tempfile.mkdtemp(prefix="mp-tiebreaker-"))

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
        if state in ("BEHIND", "DIRTY"):
            verdict, why = "PASS", f"stale PR caught pre-merge (mergeStateStatus={state})"
        elif state == "BLOCKED":
            if chk.returncode != 0:
                verdict, why = (
                    "FAIL",
                    "indeterminate: stale PR BLOCKED with non-green checks "
                    f"(gh pr checks rc={chk.returncode}) — strict:true was not exercised",
                )
            else:
                verdict, why = (
                    "PASS",
                    "stale PR caught pre-merge (BLOCKED with green checks → protection holds it)",
                )
        else:
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
                if _merge_refusal_is_protection(err):
                    verdict, why = "PASS", f"stale merge REFUSED under strict:true ({err[:120]})"
                else:
                    # Auth / rate-limit / network / head-race failures are NOT enforcement
                    # evidence — an unattributable refusal is an indeterminate probe (r1 P2).
                    verdict, why = (
                        "FAIL",
                        f"indeterminate: stale merge errored for a non-protection reason "
                        f"({err[:160]})",
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
        for scratch in (br, br2):
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
