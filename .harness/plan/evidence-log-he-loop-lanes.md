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
