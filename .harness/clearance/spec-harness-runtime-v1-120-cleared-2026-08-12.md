---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.120
cleared_at: 2026-08-12T01:45:00-07:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_2_fork_b121_provider_unreachable_name_split.md
  - ".harness/forward-register.yaml B-121 row (the B-116 F-01 raise-site evidence base)"
  - ".harness/loop_status.md RESOLVE row (b-prime agreement: codex + neutral-brief adjudicator)"
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - "loop-mode /resolve: out-of-family codex (pick salvaged from its timed-out run's own loop-state record) + neutral-brief Claude adjudicator (facts independently re-verified) — AGREEMENT on (b-prime)"
  - out-of-family `just codex-review` at this leg's PR (to convergence)
  - merge-gate 3-lens (code-touching PR)
supersedes: spec-harness-runtime-v1-119-cleared-2026-08-11.md
---

# Clearance — Spec_Harness_Runtime v1.120 (B-121 UNREACHABLE/UNREGISTERED split)

**What v1.120 changes.** The C-RT-14 fail-class taxonomy SPLITS the heterogeneous
`RT-FAIL-PROVIDER-UNREACHABLE` token: the stage-3a persistent-network sense keeps
the existing row BYTE-IDENTICAL (":3335 ping escalation — operator fixes
network/provider availability"), and a NEW permanent per-dispatch
`RT-FAIL-PROVIDER-UNREGISTERED` row carries the registry sense (provider key
absent from `ctx.providers`). C-RT-15's four registry-sense mentions
(provider-exhaustiveness invariant; failure table; the RT-FAIL-PROMPT-INJECTION-
CONFLICT comparative clause; the C-RT-16 propagation paragraph) consume the new
class; the "no new RT-FAIL-*" conformance row is re-stated as fail-class
OWNERSHIP against the post-split C-RT-14 set; the §14.6.3 E2b waiver-table member
#1 and the fail-fast bullet follow the bundled Python rename
`LLMDispatchProviderUnreachableError` → `LLMDispatchProviderUnregisteredError`.

**Why a split, not a rename.** The row's own falsifier fired at the SPEC level:
one token carried two semantics (network at :4007/:3335; registry at
:4120/:4129/:4309), and the misleading half is the operator-facing
`step-failure:` token — the demonstrated B-116 defect vector (it misled the fork
filing's §5 table and all four council voices until raise-site evidence F-01).
Only the split leaves no surface asserting a false semantic while corrupting
nothing true.

**Not a design extension beyond the routed change (X-AL-3).** The new token is
exactly the Class 2 design-substrate change the B-121 close-out routed BEFORE
code; fork doc + this marker are the paired back-flow docs for the
bundled-absorption PR (§11.4). ZERO new plan units, CXA rows, cross-axis edges,
config fields; behavior unchanged beyond the diagnostic identity.

**Register effect.** B-121 CLOSES at this leg. B-122 (the sibling bootstrap
diagnostic, closed #1316) has its warning text follow the rename in the same
cascade.
