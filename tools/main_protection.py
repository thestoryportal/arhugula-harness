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
    """owner/repo derived from THIS repository's origin remote — never from gh's ambient
    default-repo selection or GH_REPO, which could redirect the confirmed mutation to a
    different repository (codex r9 P1). Loud on failure: an empty/malformed slug would turn
    the protection request into a 404 that reads as "unprotected" (codex r4 P3)."""
    q = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    url = q.stdout.strip()
    if q.returncode != 0 or not url:
        raise SystemExit(f"repo discovery failed: {q.stderr.strip() or url!r}")
    tail = url.split(":", 1)[-1] if url.startswith("git@") else "/".join(url.split("/")[-2:])
    slug = tail.removesuffix(".git").strip("/")
    if slug.count("/") != 1 or not all(slug.split("/")):
        raise SystemExit(f"repo discovery failed: cannot parse owner/repo from {url!r}")
    return slug


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
#: GitHub's own CI app — the binding GitHub auto-assigns when a `contexts` (any-app)
#: payload is stored (live witness 2026-08-21, evidence log). Public, stable app id.
_GITHUB_ACTIONS_APP_ID = 15368

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
            # an any-app policy is never certified as an app-bound one (codex r3 P2). GET
            # expresses any-app as null, the PUT as -1 — normalize both to None (r7 P2).
            def _app(v: object) -> object:
                return None if v in (None, -1) else v

            have_pairs = sorted(
                (c["context"], _app(c.get("app_id"))) for c in rsc.get("checks") or []
            )
            want_pairs = sorted((c["context"], _app(c.get("app_id"))) for c in want_rsc["checks"])
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
            # App-binding on a contexts target: GitHub stores a `contexts` submission as
            # `checks` auto-bound to the providing app — EMPIRICALLY WITNESSED live at the
            # 2026-08-21 apply (evidence log): app_id 15368 (GitHub Actions) on every
            # check, which the original codex-r6 comparison misflagged as drift, turning
            # the fence-liveness gate RED against a correctly-applied fence. The stable
            # exact-compare therefore accepts null / -1 / the GitHub Actions app id
            # (GitHub's own representation of our any-app submission) and still flags any
            # OTHER binding — an arbitrary third-party app restriction IS a different
            # policy (fix-round r1). Fix-round r2's "distinguish an explicitly
            # Actions-bound policy from the auto-binding" is REFUTED BY MEASUREMENT:
            # both produce byte-identical GET output, so the distinction is unobservable
            # and this allowance is the maximally-strict OBSERVABLE compare. An app-bound
            # RESTORED policy still gets the strict pair-compare via the `checks` branch.
            foreign = sorted(
                c["context"]
                for c in rsc.get("checks") or []
                if c.get("app_id") not in (None, -1, _GITHUB_ACTIONS_APP_ID)
            )
            if foreign:
                out.append(
                    f"checks bound to a non-Actions app but the target policy is any-app: {foreign}"
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
        # an app-bound prior policy as an any-app policy (codex r3 P2). A null app_id in the
        # GET means "any app"; on the PUT that is the EXPLICIT -1 sentinel — omitting the
        # key would ask GitHub to auto-select an app instead (codex r7 P2).
        put_rsc = {
            "strict": bool(rsc.get("strict")),
            "checks": sorted(
                (
                    {
                        "context": c["context"],
                        "app_id": c["app_id"] if c.get("app_id") is not None else -1,
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


def _approval_digest(repo: str, current: dict | None, desired: dict) -> str:
    """Binds an operator approval to the exact (REPOSITORY, BEFORE, AFTER) triple shown at
    the dry run — the repo slug is part of the approval so an ambient-state redirect can
    never ride an approved digest (codex r9 P1)."""
    blob = json.dumps([repo, current, desired], sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def diff_report(current: dict | None, desired: dict) -> str:
    return (
        "BEFORE:\n"
        + json.dumps(current, indent=2, sort_keys=True)
        + "\nAFTER:\n"
        + json.dumps(desired, indent=2, sort_keys=True)
    )


def _loop_mode() -> bool:
    """Loop-mode is repo-wide, not worktree-local (codex r10 P2): a loop active in ANY
    linked worktree means the merge-door serialization is live and this tool's direct
    `gh pr merge` probes must not run."""
    if os.environ.get("HARNESS_LOOP") == "1" or (REPO / ".harness" / ".loop-active").exists():
        return True
    q = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    if q.returncode != 0:
        return False
    for line in q.stdout.splitlines():
        if line.startswith("worktree "):
            root = Path(line.removeprefix("worktree ").strip())
            if (root / ".harness" / ".loop-active").exists():
                return True
    return False


def _apply_lock_path() -> Path:
    """Lock in the git COMMON dir so every linked worktree of this repository shares ONE
    lock — a REPO-relative path would give each worktree its own file and void the
    serialization (codex r7 P1)."""
    q = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    common = Path(q.stdout.strip()) if q.returncode == 0 and q.stdout.strip() else REPO / ".git"
    if not common.is_absolute():
        common = REPO / common
    return common / "main-protection-apply.lock"


def _confirmed_apply(slug: str, cur: dict | None, desired: dict) -> int:
    """The digest-validated mutation transaction: evidence append → PUT → tiebreaker →
    (on FAIL) rollback to the captured pre-state. Caller holds the apply lockfile.

    `slug` is the APPROVED repository from the digest triple — every mutation in the
    transaction uses it verbatim; recomputing the target after digest validation would let
    an origin change redirect the confirmed PUT to an unapproved repository (codex r10 P1).
    """
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with EVIDENCE_LOG.open("a") as f:
        f.write(f"\n## main-protection apply {stamp}\n```\n{diff_report(cur, desired)}\n```\n")
    put_err: str | None = None
    try:
        r = subprocess.run(
            ["gh", "api", "-X", "PUT", f"repos/{slug}/branches/main/protection", "--input", "-"],
            input=json.dumps(desired),
            capture_output=True,
            text=True,
            timeout=60,
        )
        if r.returncode != 0:
            put_err = r.stderr.strip() or f"gh api exit {r.returncode}"
    except subprocess.TimeoutExpired:
        put_err = "PUT timed out client-side"
    if put_err is not None:
        # ANY reported failure is ambiguous — GitHub can accept the mutation before the
        # client errors (timeout, dropped connection, proxy 5xx). Reconcile against the
        # observed live state instead of exiting with a possibly half-applied fence and a
        # released lock (codex r8/r9 P1).
        live = current_protection()
        if live is not None and not verify(live, desired):
            print(f"provisional PUT reported failure ({put_err[:120]}) but LANDED; continuing")
        else:
            raise SystemExit(
                f"apply failed and did not land (live state unchanged): {put_err}"
            ) from None
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
    if rc == 2:
        # Probe PASSED but its cleanup is incomplete: the fence is validated — do NOT tear
        # it down over scratch leftovers — but the transaction must not read as success
        # (codex r7 P2). The leftovers are listed in the tiebreaker output above.
        raise SystemExit(
            "tiebreaker PASS but cleanup incomplete — protection PERSISTS; remove the "
            "listed scratch state by hand, then run `just main-protection-verify`"
        )
    if rc != 0:
        # CAS guard (codex r7 P1): the tiebreaker can run for many minutes — only roll back
        # if the live policy is still OUR provisional payload. A concurrent administrator
        # or process change must not be erased by this rollback.
        live = current_protection()
        if live is None or verify(live, desired):
            raise SystemExit(
                "tiebreaker FAILED but the live protection no longer matches the "
                "provisional payload (changed concurrently during the probe) — NOT rolling "
                "back; inspect `just main-protection-show` against the evidence log"
            )
        if cur is None:
            # Pre-change state was unprotected: DELETE, and VALIDATE that the deletion
            # actually landed — a failed DELETE must not be reported as a rollback (r1 P2).
            rb = _gh("api", "-X", "DELETE", f"repos/{slug}/branches/main/protection", timeout=60)
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
                f"repos/{slug}/branches/main/protection",
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


def _rollback_delete(slug: str) -> int:
    """DELETE + read-back validation: an authorization/network failure must not print
    success while protection remains live (codex r4 P2)."""
    r = _gh("api", "-X", "DELETE", f"repos/{slug}/branches/main/protection", timeout=60)
    if r.returncode != 0 or current_protection() is not None:
        print(f"rollback FAILED — protection is still live ({r.stderr.strip()[:200]})")
        return 1
    print("rolled back and verified unprotected (pre-change show is in the evidence log)")
    return 0


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
        if not a.confirm:
            slug = _repo()
            cur = current_protection()
            digest = _approval_digest(slug, cur, desired)
            print(f"repository: {slug}")
            print(diff_report(cur, desired))
            print(
                f"\nDRY RUN — nothing changed. approval digest: {digest}\n"
                "After the operator approves THIS diff, run "
                f"`just main-protection-apply-confirm {digest}`."
            )
            return 3
        # The mutation transaction is serialized by an exclusive-create lockfile: without it,
        # two confirms could both capture the same pre-state and the FAILING one's rollback
        # would tear down the SUCCEEDING one's protection (codex r4 P1). The lock is taken
        # BEFORE the pre-state read + digest validation — reading first would let a confirm
        # that waited out another's lock proceed on a stale capture (codex r5 P1). Same-host
        # scope is the real cardinality — the recipe is operator-gated on this machine.
        lock = _apply_lock_path()
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise SystemExit(
                f"another apply-confirm appears to be in flight ({lock} exists) — "
                "wait for it, or remove the lockfile if its process is dead"
            ) from None
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        try:
            slug = _repo()
            cur = current_protection()
            digest = _approval_digest(slug, cur, desired)
            print(f"repository: {slug}")
            print(diff_report(cur, desired))
            # The confirmation is bound to the exact BEFORE/AFTER pair the operator
            # approved: if the live protection or the ci.yml-derived payload changed since
            # the dry run, the digest differs and NOTHING is mutated (codex r2 P1).
            if a.approved_digest != digest:
                raise SystemExit(
                    "approval digest mismatch: the live protection or the ci.yml-derived "
                    f"payload changed since the approved diff "
                    f"(approved={a.approved_digest or '<none>'}, current={digest}) — "
                    "re-run `just main-protection-apply` and re-approve"
                )
            return _confirmed_apply(slug, cur, desired)
        finally:
            lock.unlink(missing_ok=True)
    if a.cmd == "rollback":
        if _loop_mode():
            # The guard cannot inspect the `gh api -X DELETE` this helper spawns — the
            # refusal must live here, like apply's and tiebreaker's (codex r5 P1).
            raise SystemExit("rollback refuses to run in loop mode (operator-gated)")
        # Serialized + CAS-guarded like the auto-rollback (codex r8 P2): never interleave
        # with an in-flight apply-confirm, and never delete a policy this tool did not put
        # there (a concurrently strengthened administrator policy stays untouched).
        lock = _apply_lock_path()
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise SystemExit(
                f"an apply-confirm appears to be in flight ({lock} exists) — wait for it, "
                "or remove the lockfile if its process is dead"
            ) from None
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        try:
            live = current_protection()
            if live is None:
                print("main is already unprotected — nothing to roll back")
                return 0
            if verify(live, desired):
                raise SystemExit(
                    "live protection does not match this tool's §2 payload — refusing to "
                    "delete a policy this tool did not apply; use `gh api` directly if "
                    "that is really intended"
                )
            print(
                "NOTE: DELETE restores the unprotected (404) pre-state; if the evidence "
                "log's most recent BEFORE block shows a prior policy, restore THAT payload "
                "instead of deleting (codex r10 P2)"
            )
            return _rollback_delete(_repo())
        finally:
            lock.unlink(missing_ok=True)
    # tiebreaker: scratch PR under strict:true + stale-refresh-branch check (HE-1 O4; C10-T8).
    if _loop_mode():
        raise SystemExit("tiebreaker is a live probe; run outside loop mode")
    # Serialized with apply/rollback (codex r9 P2): the probe advances main and samples the
    # live policy — overlapping an in-flight mutation transaction would invalidate either.
    lock = _apply_lock_path()
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise SystemExit(
            f"an apply-confirm/rollback appears to be in flight ({lock} exists) — wait for "
            "it, or remove the lockfile if its process is dead"
        ) from None
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
    try:
        return tiebreaker()
    finally:
        lock.unlink(missing_ok=True)


#: Three-way refusal attribution (codex r1/r3/r4 P2). "strict" signatures name the
#: base-freshness/status-check mechanism ITSELF — broader protection wording ("branch
#: protection", "review is required") can come from reviews, rulesets, or other rules that
#: would refuse the merge even without strict:true, so it sits in the "generic" tier with
#: the mergeability errors and counts as enforcement evidence only when the PR's own
#: mergeStateStatus independently read BEHIND (the strict staleness reading) AND the §2
#: fence was verified live at probe start; anything else (auth/rate-limit/network/
#: head-race) is an indeterminate probe, never a PASS.
_STRICT_REFUSAL_SIGS = (
    "required status check",
    "behind",
)
_GENERIC_MERGEABILITY_SIGS = (
    "not mergeable",
    "merge state",
    "branch protection",
    "protected branch",
    "review is required",
    # "base branch" also appears in generic ruleset/policy/base-race wording — it earns a
    # PASS only alongside the independent BEHIND reading (codex r10 P2).
    "base branch",
)


def _classify_merge_refusal(stderr: str) -> str:
    """'strict' | 'generic' | 'transport' — see the signature-tier comment above."""
    low = stderr.lower()
    if any(s in low for s in _STRICT_REFUSAL_SIGS):
        return "strict"
    if any(s in low for s in _GENERIC_MERGEABILITY_SIGS):
        return "generic"
    return "transport"


def _watch_checks(prno: str, cwd: Path, required: list[str], attempts: int = 8) -> bool:
    """`gh pr checks --watch` hardened two ways (both live-witnessed / fix-round r1):
    (a) not-yet-started retry — the watch exits 1 with "no checks reported" when polled
    before CI registers any check-run on a fresh branch (scratch PR #1419); that is
    never a red — re-poll with backoff; (b) registration-complete validation — a green
    watch during PARTIAL registration must not count until every required blocking
    context has actually reported, else a later refusal for a missing required check
    could masquerade as strict enforcement."""
    for _ in range(attempts):
        w = subprocess.run(
            ["gh", "pr", "checks", prno, "--watch"],
            capture_output=True,
            text=True,
            timeout=1800,
            cwd=cwd,
        )
        blob = (w.stdout + w.stderr).lower()
        if w.returncode == 0:
            names = subprocess.run(
                ["gh", "pr", "checks", prno, "--json", "name", "--jq", ".[].name"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=cwd,
            )
            reported = set(names.stdout.splitlines())
            if names.returncode == 0 and set(required) <= reported:
                return True
            time.sleep(20)
            continue
        if "no checks reported" in blob:
            time.sleep(20)
            continue
        return False
    return False


def tiebreaker() -> int:
    """C-HE-08 §4 (HE-1 O4; C10-T8): exercise strict:true on a scratch PR, then the
    load-bearing parameter — a refresh-shaped PR branched from the since-superseded main is
    CAUGHT pre-merge or fast-forwards cleanly.

    Runs in an ISOLATED temporary worktree (never switches the operator's checkout; never
    picks up staged changes — Codex round-3 P1) and compares the stale landing against the
    main SHA captured BEFORE that merge."""
    # Fence-liveness precondition (codex r4 P2): a clean fast-forward landing is ALSO what
    # happens with no protection at all, so the probe witnesses strict:true only if the §2
    # fence is verified live first — otherwise every arm of the verdict is meaningless.
    required_contexts = blocking_contexts()
    live_problems = verify(current_protection(), desired_payload(required_contexts))
    if live_problems:
        print(
            "tiebreaker: FAIL — the §2 fence is not live "
            f"({'; '.join(live_problems[:3])}); the probe cannot witness strict:true"
        )
        return 1
    # PID suffix: one-second timestamp uniqueness is not enough — concurrent tiebreakers
    # must never collide on (or GC) each other's scratch branches (codex r3 P2).
    ts = f"{time.strftime('%Y%m%d%H%M%S', time.gmtime())}-{os.getpid()}"
    br = f"mp-tiebreaker-{ts}"
    br2 = f"mp-tiebreaker-stale-{ts}"
    wt = Path(tempfile.mkdtemp(prefix="mp-tiebreaker-"))
    created: list[str] = []  # only branches THIS invocation pushed are GC'd (codex r3 P2)
    created_local: list[str] = []  # local refs are repo-global; GC'd after worktree removal

    def sh(*c: str, cwd: Path | None = None) -> str:
        q = subprocess.run(list(c), capture_output=True, text=True, timeout=180, cwd=cwd or wt)
        if q.returncode != 0:
            raise SystemExit(f"{' '.join(c)}: {q.stderr.strip()}")
        return q.stdout.strip()

    def merge_attempt(prno: str, head: str) -> tuple[bool, str]:
        """(merged, stderr) — RECONCILED against authoritative PR state: `gh pr merge` can
        time out or error AFTER GitHub lands the merge, and treating that as a refusal
        would roll a persisted protection back over an already-advanced main (codex r5 P1).
        """
        err = ""
        try:
            mm = subprocess.run(
                ["gh", "pr", "merge", prno, "--squash", "--match-head-commit", head],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=wt,
            )
            err = mm.stderr.strip()
            if mm.returncode == 0:
                return True, err
        except subprocess.TimeoutExpired:
            err = "gh pr merge timed out"
        st = subprocess.run(
            ["gh", "pr", "view", prno, "--json", "state", "--jq", ".state"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=wt,
        )
        return (st.returncode == 0 and st.stdout.strip() == "MERGED"), err

    def run() -> int:
        # Setup runs INSIDE the cleanup scope: a failure in fetch/worktree-add must still
        # reach the finally-block GC — the temp dir and any partial worktree registration
        # are its to reap (codex r9 P3).
        sh("git", "fetch", "-q", "origin", cwd=REPO)
        sh("git", "worktree", "add", "-q", "--detach", str(wt), "origin/main", cwd=REPO)
        base = sh("git", "rev-parse", "origin/main")
        sh("git", "checkout", "-q", "-b", br)
        created_local.append(br)
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
            "--base",
            "main",
        )
        pr = url.rsplit("/", 1)[-1]
        print(f"tiebreaker: waiting for checks on #{pr} (strict:true requires up-to-date + green)")
        # Same 1800 s allowance as the stale PR's watch — sh()'s 180 s would misread any
        # healthy CI run longer than three minutes as a tiebreaker failure (codex r6 P2).
        if not _watch_checks(pr, wt, required_contexts):
            print("precondition failed: scratch PR checks did not go green")
            return 1
        head = sh("git", "rev-parse", "HEAD")
        merged, merr = merge_attempt(pr, head)
        if not merged:
            print(f"precondition failed: scratch merge refused under strict:true ({merr})")
            return 1
        # The load-bearing parameter: a refresh-shaped PR branched from the since-superseded main.
        sh("git", "checkout", "-q", "-b", br2, base)
        created_local.append(br2)
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
            "--base",
            "main",
        )
        pr2 = url2.rsplit("/", 1)[-1]
        # BLOCKED is ambiguous straight after creation — pending or failing required checks
        # also report BLOCKED, so an immediate read could "PASS" without strict:true ever
        # being exercised (codex r1 P1). Let the stale PR's checks settle first, then read.
        stale_green = _watch_checks(pr2, wt, required_contexts)
        state = sh(
            "gh", "pr", "view", pr2, "--json", "mergeStateStatus", "--jq", ".mergeStateStatus"
        )
        if not stale_green:
            # Non-green checks contaminate the probe: any merge refusal would be attributable
            # to failing checks rather than base-staleness, so strict:true is not isolable.
            verdict, why = (
                "FAIL",
                f"indeterminate: stale PR checks did not go green "
                f"(mergeStateStatus={state}) — strict:true not exercised",
            )
        else:
            # EXERCISE the merge rather than inferring from mergeStateStatus — BEHIND/BLOCKED
            # are advisory readings, and only an actual protection-attributed refusal (or a
            # clean fast-forward landing) proves the load-bearing parameter (codex r2 P1).
            sh("git", "fetch", "-q", "origin")
            pre = sh("git", "rev-parse", "origin/main")  # main BEFORE the stale merge
            head2 = sh("git", "rev-parse", "HEAD")
            merged2, err = merge_attempt(pr2, head2)
            if not merged2:
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
                # Validate the PR's OWN merge commit — the origin/main tip can have been
                # advanced by another lane between the merge and this read, and judging by
                # the tip would fail a correct landing and roll the protection back
                # (codex r6 P1).
                oid = sh(
                    "gh", "pr", "view", pr2, "--json", "mergeCommit", "--jq", ".mergeCommit.oid"
                )
                sh("git", "fetch", "-q", "origin")
                first_parent = sh("git", "rev-parse", f"{oid}^1")
                # Another lane may advance main between the `pre` sample and GitHub creating
                # the squash commit — a correct landing then has a DESCENDANT of `pre` as its
                # first parent, not `pre` itself; only an off-lineage parent is a failure
                # (codex r8 P2).
                on_lineage = first_parent == pre or (
                    subprocess.run(
                        ["git", "merge-base", "--is-ancestor", pre, first_parent],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=wt,
                    ).returncode
                    == 0
                )
                if on_lineage:
                    # A clean fast-forward is ALSO what no-protection produces — re-verify
                    # the fence survived the whole probe before letting this arm PASS
                    # (codex r8 P2; the refusal arm carries its own enforcement witness).
                    still = verify(current_protection(), desired_payload(blocking_contexts()))
                    verdict, why = (
                        ("PASS", "stale PR fast-forwarded cleanly onto the pre-merge lineage")
                        if not still
                        else (
                            "FAIL",
                            f"fence changed during the probe ({'; '.join(still[:3])}) — "
                            "the fast-forward landing does not witness strict:true",
                        )
                    )
                else:
                    verdict, why = (
                        "FAIL",
                        f"stale PR landed off the pre-merge lineage "
                        f"(merge commit {oid[:12]} first parent {first_parent[:12]} "
                        f"not descended from {pre[:12]})",
                    )
        print(f"tiebreaker: {verdict} — {why}")
        # No explicit pr2 close here: closing with --delete-branch would delete the remote
        # ref BEFORE the finally-block's documented worktree→local→remote order and re-open
        # the leak it prevents (codex r6 P2); the finally-block's remote-ref deletion
        # auto-closes the still-open PR.
        return 0 if verdict == "PASS" else 1

    cleanup_failures: list[str] = []
    try:
        result = run()
    finally:
        # External-state GC on EVERY exit path — a failed probe must not leave scratch PRs
        # open, remote branches, local refs, or the temporary worktree behind (codex r1 P3):
        # deleting a remote branch auto-closes its open PR, and an already-deleted/merged
        # branch makes this a no-op. ORDER MATTERS (codex r5 P2): the worktree is removed
        # FIRST (it holds a checkout of a scratch branch and its -u upstream config; remote
        # refs deleted first would make the remover classify that upstream as unresolvable
        # local state and refuse), then local refs, then remote refs. Failures are REPORTED,
        # not swallowed — silent GC failure would contradict the cleanup contract while
        # looking identical to success (codex r4 P3).
        def _gc_run(cmd: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
            # A timeout in ONE cleanup step must not abort the remaining steps and bypass
            # the failure accounting (codex r8 P2).
            try:
                return subprocess.run(
                    cmd, capture_output=True, text=True, timeout=timeout, cwd=REPO
                )
            except (subprocess.TimeoutExpired, OSError) as exc:
                return subprocess.CompletedProcess(cmd, 124, "", f"{exc!r}")

        wtrm = _gc_run(
            ["bash", str(REPO / "tools" / "hooks" / "safe-worktree-remove.sh"), str(wt)],
            120,
        )
        if wtrm.returncode != 0:
            cleanup_failures.append(f"temporary worktree {wt} not removed")
            print(
                f"WARNING: cleanup incomplete — temporary worktree {wt} was not removed "
                f"({wtrm.stderr.strip()[:120]})"
            )
            # Deleting local/remote refs under a RETAINED worktree would strand it with
            # unresolvable upstreams — exactly the state the ordering exists to prevent.
            # Leave the refs; they are accounted as leftovers with the worktree (r9 P2).
            for leftover in [*created_local, *created]:
                cleanup_failures.append(f"ref {leftover} left for the retained worktree")
            created_local.clear()
            created.clear()
        for local in created_local:
            lgc = _gc_run(["git", "branch", "-D", local], 60)
            if lgc.returncode != 0 and "not found" not in lgc.stderr:
                cleanup_failures.append(f"local branch {local} not deleted")
                print(
                    f"WARNING: cleanup incomplete — local branch {local} was not deleted "
                    f"({lgc.stderr.strip()[:120]})"
                )
        for scratch in created:
            gc = _gc_run(["git", "push", "-q", "origin", "--delete", scratch], 60)
            if gc.returncode != 0 and "remote ref does not exist" not in gc.stderr:
                cleanup_failures.append(f"remote branch origin/{scratch} (and its PR) not deleted")
                print(
                    f"WARNING: cleanup incomplete — could not delete origin/{scratch} "
                    f"({gc.stderr.strip()[:120]}); delete it (and its PR) by hand"
                )
    if result == 0 and cleanup_failures:
        # The probe PASSED but the every-exit cleanup contract was not met — that must not
        # read as a successful transaction (codex r7 P2). rc 2 lets the apply keep the
        # VALIDATED fence while still exiting nonzero with the leftovers listed.
        print("tiebreaker: PASS but cleanup incomplete — " + "; ".join(cleanup_failures))
        return 2
    return result


if __name__ == "__main__":
    raise SystemExit(main())
