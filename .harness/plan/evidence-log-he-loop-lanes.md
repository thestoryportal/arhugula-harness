# Evidence log — spec-he-loop-lanes operator-gated live steps

*Append-only. Live halves of operator-gated units record their evidence here: the
`main_protection.py apply --confirm` path appends its before/after diff automatically;
tiebreaker PASS lines and pre-change `show` output are recorded by the session that runs
the gate (C-HE-08 §2–§5, U-HE-27 Step 5).*

## U-HE-27 landing record — B-190 bounded by the C-HE-08 §2 server fence (2026-08-21)

Per B-190's close-out step (2) (`.harness/post-phase-8-forward-register.md`) and the
post-#1417 roadmap directive: with `tools/main_protection.py` + the
`just main-protection-{show,apply,rollback,tiebreaker,verify}` recipes landed at U-HE-27,
B-190's register-and-held residual classes are **bounded by the server-side fence per
invariant R-20** (protection is independent of any bug in the client guard):

- **P1** — metachar-bearing remote names (`o'igin`) defeating the client dequote-then-lookup;
- **P2** — git-config TOCTOU between the bare-push config sample and push execution;
- **lens P3 (folded at this landing, from the PR #1417 merge-gate witness lens)** — the
  bare-push predicate's `branch.<b>.remote` resolution tier carries no dedicated
  guard-suite witness; misresolution in that untested tier is the same
  client-parser-residual family.

All three presume adversarial local git-config write (config-write = code-write in this
workspace) and sit outside the client predicate's threat model. The fence closes each for
`main` regardless of client parsing. No client-side narrowing is owed (non-convergent by
measurement, U-HE-26 codex rounds r1–r10).

**Status: PENDING-APPLY.** This entry records the LANDING half only (code + recipes +
§8.1 phase0 row); as of this landing `main` is still unprotected (`show` → `null`,
`verify` → RED `unprotected (404)`) and the fence is NOT yet live, so B-190's bound is
**not yet in force**. It comes into force only when the operator-approved
`apply --confirm` (digest-bound diff) and its §4 tiebreaker PASS are appended below;
`just main-protection-verify` GREEN is the standing observable from that point (codex r2
P2: this file must not read as claiming the bound before the live evidence exists).

## main-protection apply 2026-08-22T02:24:03Z
```
BEFORE:
null
AFTER:
{
  "allow_deletions": false,
  "allow_force_pushes": false,
  "enforce_admins": true,
  "required_linear_history": false,
  "required_pull_request_reviews": null,
  "required_status_checks": {
    "contexts": [
      "CLAUDE.md citations (I-1 resolution gate) \u2014 blocking",
      "Codex context guard (anti-rot gate) \u2014 blocking",
      "Q1 review gate (structured artifact) \u2014 blocking",
      "Q3 evidence + closure gate \u2014 blocking",
      "arc ledger (tally gate) \u2014 blocking",
      "clearance corpus (frontmatter gate) \u2014 blocking",
      "pyright (strict) \u2014 blocking",
      "pytest (all axis packages) \u2014 blocking",
      "ruff (lint + format) \u2014 blocking",
      "semantic overlay (drift gate) \u2014 blocking",
      "substitution ledger (tally gate) \u2014 blocking",
      "tools/ test coverage guard + codex-loop tests \u2014 blocking"
    ],
    "strict": true
  },
  "restrictions": null
}
```

## U-HE-27 Step-5 operator gate — EXECUTED (2026-08-21/22 UTC)

Operator approved via one AskUserQuestion ("Apply now"). Record of the live sequence:

1. **Pre-change `show`:** `null` (404, unprotected) — matches the plan's expectation.
2. **Dry-run `apply`:** printed `repository: thestoryportal/arhugula-harness`, the
   BEFORE(null)/AFTER(§2 payload, 12 "— blocking" contexts) diff, approval digest
   `09582edbd7a3f2b2`. (The 13th grep hit for "— blocking" in ci.yml is a STEP name
   inside the pytest job, not a job — the 12-context derivation is correct.)
3. **`apply-confirm 09582edbd7a3f2b2`:** provisional PUT LANDED (protection live with the
   approved settings). The in-run tiebreaker then FAILED at its fence-liveness gate on a
   comparator defect, not a fence defect: GitHub stores a `contexts` submission as
   `checks` auto-bound to the providing app (`app_id` 15368, GitHub Actions), and the
   codex-r6 "app-bound vs any-app" check flagged our own payload's round-trip as drift.
   The CAS rollback guard then (correctly) refused to roll back a live policy that no
   longer verified as the provisional payload — **fence kept**, exit nonzero. Empirical
   falsification of the r6 finding's premise; comparator fixed same-session
   (name-compare for contexts targets; `test_verify_accepts_github_auto_app_binding_for_contexts_target`).
4. **`verify` after the fix: PASS** — live policy exact-compares clean against the §2
   payload (strict:true, 12 contexts, enforce_admins, no force-push/deletion, reviews
   null, restrictions null, optional controls all False).
5. **Tiebreaker attempt 1 (scratch PR #1419):** failed at the checks precondition —
   `gh pr checks --watch` exits 1 with "no checks reported" when polled before CI
   registers check-runs (the standing benign-nonzero class). GC closed #1419 + deleted
   its branch correctly. Watch fixed with a not-yet-started retry (8×20s backoff).
6. **Tiebreaker attempt 2 (scratch PRs #1420/#1421): PASS** — scratch merge landed under
   strict:true; the stale refresh-shaped PR fast-forwarded cleanly onto the pre-merge
   lineage with the fence re-verified live inside the PASS arm. Cleanup clean (exit 0,
   no rc-2 leftovers).

**C-HE-08 §2–§5 fully discharged. B-190's bound is IN FORCE** (supersedes the
PENDING-APPLY status above): the server fence is live and verified; `just
main-protection-verify` GREEN is the standing observable. Residuals remain B-191.
